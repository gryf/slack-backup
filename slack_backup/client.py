"""
Create backup for certain date for specified channel in slack
"""
import logging
from datetime import datetime

import slackclient

from slack_backup import db
from slack_backup.objects import User, Channel, Purpose, Topic


class Client(object):
    def __init__(self, token, dbfilename=None):
        self.slack = slackclient.SlackClient(token)
        self.engine = db.connect(dbfilename)
        self.session = db.Session()
        self.q = self.session.query

    def update_history(self, selected_channels=None, from_date=0):

        self._update_users()
        self._update_channels()

        channels = self._get_channel_list()
        if selected_channels:
            selected_channels = [c for c in channels
                                 if c.name in selected_channels]
        else:
            selected_channels = channels

        for channel in selected_channels:
            history = []
            latest = 0

            while True:
                messages, latest = self._get_channel_history(channel, latest)
                # TODO: merge messages witihn a channel
                if latest is None:
                    break
                for msg in messages:
                    history.append(msg)

        self.session.close()
        return history

    def _get_channel_history(self, channel, latest='now'):
        result = self.slack.api_call("channels.history",
                                     channel=channel.slackid, count=1000,
                                     latest=latest)

        if not result.get("ok"):
            logging.error(result['error'])
            return None, None

        if result['messages']:
            return result['messages'], result['messages'][-1]['ts']
        else:
            return result['messages'], None

    def _get_channel_list(self):
        result = self.slack.api_call("channels.list")

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        return [Channel(chan) for chan in result['channels']]

    def _update_users(self):
        """Fetch and update user list with current state in db"""
        result = self.slack.api_call("users.list", presence=0)

        if not result.get("ok"):
            logging.error(result['error'])
            return

        for user_data in result['members']:
            user = self.q(User).\
                filter(User.slackid == user_data['id']).one_or_none()

            if user:
                user.update(user_data)
            else:
                user = User(user_data)
                self.session.add(user)
                self.session.flush()

        self.session.commit()

    def _get_create_obj(self, data, classobj, channel):
        """
        Return object if exist in appropriate table (Topic or Purpose),
        compared to the data provided, create it otherwise.
        """
        user = self.q(User).filter(User.slackid ==
                                   data['creator']).one_or_none()
        if not user:
            return

        obj = self.q(classobj).\
            filter(classobj.last_set ==
                   datetime.fromtimestamp(data['last_set'])).\
            filter(classobj.value == data['value']).\
            filter(classobj.creator_id == user.id).one_or_none()

        if not obj:
            # break channel relation
            for obj in self.q(classobj).filter(classobj.channel ==
                                               channel).all():
                obj.channel = None

            # create new object
            obj = classobj(data)
            obj.creator = user
            self.session.flush()

        return obj

    def _update_channel(self, channel, data):
        channel.update(data)
        channel.user = self.q(User).filter(User.slackid ==
                                           data['created']).one_or_none()
        channel.purpose = self._get_create_obj(data['purpose'], Purpose,
                                               channel)
        channel.topic = self._get_create_obj(data['topic'], Topic, channel)
        self.session.flush()

    def _update_channels(self):
        """Fetch and update user list with current state in db"""
        result = self.slack.api_call("channels.list", presence=0)

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        for channel_data in result['channels']:
            channel = self.q(Channel).filter(Channel.slackid ==
                                             channel_data['id']).one_or_none()

            if not channel:
                channel = Channel()
                self.session.add(channel)

            self._update_channel(channel, channel_data)

        self.session.commit()
