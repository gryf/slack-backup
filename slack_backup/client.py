"""
Create backup for certain date for specified channel in slack
"""
from datetime import datetime
import getpass
import logging

import slackclient

from slack_backup import db
from slack_backup import objects as o
from slack_backup import download


class Client(object):
    """
    This class is intended to provide an interface for getting, storing and
    querying data fetched out using Slack API.
    """
    def __init__(self, args):
        self.slack = slackclient.SlackClient(args.token)
        self.engine = db.connect(args.dbfilename)
        self.session = db.Session()
        self.selected_channels = args.channels
        self.user = args.user
        self.password = args.password
        if not self.user and not self.password:
            logging.warning('No media will be downloaded, due to not '
                            'providing credentials for a slack account')
        elif not self.user and self.password:
            logging.warning('No media will be downloaded, due to not '
                            'providing username for a slack account')
        elif self.user and not self.password:
            self.password = getpass.getpass(prompt='Provide password for '
                                            'your slack account: ')
        self.q = self.session.query
        self.dld = download.Download(args.user, args.password, args.team)

    def update(self):
        """
        Perform an update, store data to db
        """
        self.dld.authorize()
        self.update_users()
        self.update_channels()
        self.update_history()

    def update_channels(self):
        """Fetch and update channel list with current state in db"""
        result = self._channels_list()

        if not result:
            return

        for channel_data in result:
            channel = self.q(o.Channel).\
                filter(o.Channel.slackid == channel_data['id']).one_or_none()

            if not channel:
                channel = o.Channel()
                self.session.add(channel)

            self._update_channel(channel, channel_data)

        self.session.commit()

    def update_users(self):
        """Fetch and update user list with current state in db"""
        result = self.slack.api_call("users.list", presence=0)

        if not result.get("ok"):
            logging.error(result['error'])
            return

        for user_data in result['members']:
            user = self.q(o.User).\
                filter(o.User.slackid == user_data['id']).one_or_none()

            if user:
                user.update(user_data)
            else:
                user = o.User(user_data)
                self.session.add(user)
                self.session.flush()

        self.session.commit()

    def update_history(self):
        """
        Get the latest or all messages out of optionally selected channels
        """

        all_channels = self.q(o.Channel).all()
        if self.selected_channels:
            channels = [c for c in all_channels
                        if c.name in self.selected_channels]
        else:
            channels = all_channels

        for channel in channels:
            latest = self.q(o.Message).\
                filter(o.Message.channel == channel).\
                order_by(o.Message.ts.desc()).first()
            latest = latest and latest.ts or 0

            while True:
                messages, latest = self._channels_history(channel, latest)

                for msg in messages:
                    self._create_message(msg, channel)

                if latest is None:
                    break

        self.session.commit()

    def _create_message(self, data, channel):
        """
        Create message with corresponding possible metadata, like reactions,
        files etc.
        """
        message = o.Message(data)
        message.user = self.q(o.User).\
            filter(o.User.slackid == data['user']).one()
        message.channel = channel

        if 'reactions' in data:
            for reaction_data in data['reactions']:
                message.reactions.append(o.Reaction(reaction_data))

        if data.get('subtype') == 'file_share':
            message.file = o.File()
            if data['file']['is_external']:
                message.file.url = data['file']['url_private']
            else:
                priv_url = data['file']['url_private_download']
                message.file.url = self.dld.get_local_url(priv_url)

        self.session.add(message)

    def _get_create_obj(self, data, classobj, channel):
        """
        Return object if exist in appropriate table (Topic or Purpose),
        compared to the data provided, create it otherwise.
        """
        if not data['value']:
            return

        user = self.q(o.User).filter(o.User.slackid ==
                                     data['creator']).one_or_none()

        obj = self.q(classobj).\
            filter(classobj.last_set ==
                   datetime.fromtimestamp(data['last_set'])).\
            filter(classobj.value == data['value']).\
            filter(classobj.creator == user).one_or_none()

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
        """Update a channel with provided data"""
        channel.update(data)
        channel.user = self.q(o.User).filter(o.User.slackid ==
                                             data['creator']).one_or_none()
        channel.purpose = self._get_create_obj(data['purpose'], o.Purpose,
                                               channel)
        channel.topic = self._get_create_obj(data['topic'], o.Topic, channel)
        self.session.flush()

    def _channels_list(self):
        """
        Get channel list using Slack API. Return list of channel data or None
        in case of error.
        """
        result = self.slack.api_call("channels.list")

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        return result['channels']

    def _users_list(self):
        """
        Get users list using Slack API. Return list of channel data or None
        in case of error.
        """
        result = self.slack.api_call("users.list", presence=0)

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        return result['members']

    def _channels_history(self, channel, latest):
        """
        Get list of messages using Slack API. Return tuple containing:
         - list of messages data and returned timestramp if has_more is set
           to true,
         - list of messages data and None if has_more is set to false,
         - empty list and None if there is no messages
        """
        result = self.slack.api_call("channels.history",
                                     channel=channel.slackid, count=1000,
                                     oldest=latest)

        if not result.get("ok"):
            logging.error(result['error'])
            return None, None

        if result['messages']:
            if result['has_more']:
                # TODO: this one might be not true, if API will return
                # messages not sorted by timestamp in descending order
                return result['messages'], result['messages'][0]['ts']
            else:
                return result['messages'], None

        return [], None
