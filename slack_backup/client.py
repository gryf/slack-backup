"""
Create backup for certain date for specified channel in slack
"""
import logging

import slackclient

from slack_backup import db
from slack_backup import objects as o


class Client(object):
    def __init__(self, token, dbfilename=None):
        self.slack = slackclient.SlackClient(token)
        self.engine = db.connect(dbfilename)
        self.session = db.Session()

    def get_hisotry(self, selected_channels=None, from_date=0):

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

        return [o.Channel(chan) for chan in result['channels']]

    def _update_users(self):
        """Fetch and update user list with current state in db"""
        result = self.slack.api_call("users.list", presence=0)

        if not result.get("ok"):
            logging.error(result['error'])
            return

        for user_data in result['members']:
            user = self.session.query(o.User).\
                filter(o.User.slackid == user_data['id']).one_or_none()

            if user:
                user.update(user_data)
            else:
                user = o.User(user_data)
                self.session.add(user)
                self.session.flush()

        self.session.commit()

    def get_create_obj(self, data, classobj, channel):
        """
        Return object if exist in appropriate table (class), compared to the
        data provided, create it otherwise.
        """
        user = self.session.query(o.User).\
            filter(o.User.slackid == data['creator']).one_or_none()
        if not user:
            return

        obj = self.session.query(classobj).\
            filter(classobj.last_set == data['last_set']).\
            filter(classobj.value == data['last_set']).\
            filter(classobj.creator_id == user.id).one_or_none()

        if not obj:
            obj = classobj(data)
            obj.creator = user
            obj.channel = channel
            self.session.add(obj)
            self.session.flush()

        return obj

    def _update_channels(self):
        """Fetch and update user list with current state in db"""
        result = self.slack.api_call("channels.list", presence=0)

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        for channel_data in result['channels']:
            channel = self.session.query(o.Channel).\
                filter(o.Channel.slackid == channel_data['id']).one_or_none()

            if channel:
                channel.update(channel_data)
                channel.user = self.session.query(o.User).\
                    filter(o.User.slackid ==
                           channel_data['created']).one_or_none()
                # channel.purpose = self.get_create_obj(channel_data['purpose'],
                                                      # o.Purpose, channel)
                # channel.topic = self.get_create_obj(channel_data['topic'],
                                                    # o.Topic, channel)
            else:
                channel = o.Channel(channel_data)
                # channel.purpose = self.get_create_obj(channel_data['purpose'],
                                                      # o.Purpose, channel)
                # channel.topic = self.get_create_obj(channel_data['topic'],
                                                    # o.Topic, channel)
                self.session.add(channel)
                self.session.flush()

        self.session.commit()
