"""
Create backup for certain date for specified channel in slack
"""
from datetime import datetime
import getpass
import json
import logging
import os

import slackclient
import sqlalchemy.orm.exc

from slack_backup import db
from slack_backup import objects as o
from slack_backup import download
from slack_backup import reporters


class Client(object):
    """
    This class is intended to provide an interface for getting, storing and
    querying data fetched out using Slack API.
    """
    def __init__(self, args):
        if 'token' in args:
            self.slack = slackclient.SlackClient(args.token)
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
            dbpath = self._get_asset_dir(args.database)
            self.downloader = download.Download(args, dbpath)
        self.engine = db.connect(args.database)
        self.session = db.Session()
        self.selected_channels = args.channels
        self.q = self.session.query

        if 'format' in args:
            self.reporter = reporters.get_reporter(args, self.q)

    def update(self):
        """
        Perform an update, store data to db
        """
        self.downloader.authorize()
        self.update_users()
        self.update_channels()
        self.update_history()

    def update_channels(self):
        """Fetch and update channel list with current state in db"""
        logging.info("Fetching and update channels information in DB")
        result = self._channels_list()

        if not result:
            return

        for data in result:
            channel = self.q(o.Channel).\
                filter(o.Channel.slackid == data['id']).one_or_none()

            if not channel:
                channel = o.Channel()
                self.session.add(channel)

            self._update_channel(channel, data)

        self.session.commit()

    def update_users(self):
        """Fetch and update user list with current state in db"""
        result = self._users_list()

        if not result:
            return

        for user_data in result:
            user = self.q(o.User).\
                filter(o.User.slackid == user_data['id']).one_or_none()

            if user:
                user.update(user_data)
            else:
                user = o.User(user_data)
                self.session.add(user)
                self.session.flush()

            if user.profile.image_original:
                user.profile.image_path = self.downloader.\
                    download(user.profile.image_original, 'avatar')

        self.session.commit()

    def update_history(self):
        """
        Get the latest or all messages out of optionally selected channels
        """
        logging.info("Fetching and storing messages in DB")

        all_channels = self.q(o.Channel).all()
        if self.selected_channels:
            channels = [c for c in all_channels
                        if c.name in self.selected_channels]
        else:
            channels = all_channels

        for channel in channels:
            logging.info("Getting messages for channel `%s'", channel.name)
            latest = self.q(o.Message).\
                filter(o.Message.channel == channel).\
                order_by(o.Message.ts.desc()).first()
            # NOTE(gryf): Trick out the API, which by default (latest and
            # oldest parameters set to 0) return certain amount of latest
            # messages, while we'd like to have it from the beginning of the
            # available history, if there is no database records available. In
            # that case value of 1 here will force the API to get messages
            # starting from first January 1970.
            latest = latest and latest.ts or 1

            while True:
                logging.debug("Fetching another portion of messages")
                messages, latest = self._channels_history(channel, latest)

                for msg in messages:
                    self._create_message(msg, channel)

                if latest is None:
                    break

        self.session.commit()

    def generate_history(self):
        """
        Return a history accumulated in DB into desired format. Special format
        """
        self.reporter.generate()

    def _get_user(self, data):
        """
        Return an User object. It can be regular one, or a bot. In case of
        bot, check if it exists in db, and in case of failure - create it,
        since bots are not returned by user.list API method.
        """
        try:
            return self.q(o.User).filter(o.User.slackid == data['user']).one()
        except KeyError:
            pass

        try:
            return self.q(o.User).filter(o.User.slackid ==
                                         data['comment']['user']).one()
        except KeyError:
            pass

        try:
            return self.q(o.User).filter(o.User.slackid ==
                                         data['bot_id']).one()
        except KeyError:
            pass
        except sqlalchemy.orm.exc.NoResultFound:
            result = self.slack.api_call('bots.info', bot=data['bot_id'])
            if not result.get("ok"):
                logging.error(result['error'])
                return None

            user = o.User(result['bot'])
            user.real_name = result['bot']['name']
            self.session.add(user)
            self.session.flush()
            return user

        raise ValueError('Cannot identify user out of data:' + str(data))

    def _create_message(self, data, channel):
        """
        Create message with corresponding possible metadata, like reactions,
        files etc.
        """
        if data['type'] != 'message':
            logging.info("Skipping message of type `%s'.", data['type'])
            return

        logging.debug('Message data: %s', json.dumps(data))

        user = self._get_user(data)

        if not any((data.get('attachments'), data['text'].strip())):
            logging.info("Skipping message from `%s' since it's empty",
                         user.name)
            return

        message = o.Message(data)
        message.channel = channel
        message.user = user

        if data.get('is_starred'):
            message.is_starred = True

        if 'reactions' in data:
            for reaction_data in data['reactions']:
                message.reactions.append(o.Reaction(reaction_data))

        if data.get('subtype') == 'file_share':
            self._file_data(message, data['file'], data['file']['is_external'])
        elif data.get('subtype') == 'pinned_item':
            if data.get('attachments'):
                self._att_data(message, data['attachments'])
            elif data.get('item'):
                self._file_data(message, data['item'],
                                data['item']['is_external'])
        elif data.get('attachments'):
            self._att_data(message, data['attachments'])

        self.session.add(message)

    def _file_data(self, message, data, is_external=True):
        """
        Process file data. Could be either represented as 'file' object or
        'item' object in case of pinned items
        """
        message.file = o.File(data)
        if data.get('is_starred'):
            message.is_starred = True

        if is_external:
            logging.debug("Found external file `%s'", data['url_private'])
            message.file.url = data['url_private']
        else:
            logging.debug("Found internal file `%s'",
                          data['url_private_download'])
            priv_url = data['url_private_download']
            message.file.filepath = self.downloader.download(priv_url, 'file')
        self.session.add(message.file)

    def _att_data(self, message, data):
        """
        Process attachments
        """
        for att in data:
            attachment = o.Attachment(att)
            message.attachments.append(attachment)

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
        logging.info("Update channel `%s' information in DB", data['name'])

        channel.update(data)
        channel.user = self.q(o.User).filter(o.User.slackid ==
                                             data['creator']).one_or_none()
        channel.purpose = self._get_create_obj(data['purpose'], o.Purpose,
                                               channel)
        channel.topic = self._get_create_obj(data['topic'], o.Topic, channel)
        self.session.flush()

    def _get_asset_dir(self, database):
        """
        Get absolute assets directory using sqlite database path as a
        reference.
        """
        if not database:
            return 'assets'

        path = os.path.dirname(database)
        return os.path.join(path, 'assets')

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
        logging.info("Fetching and updating user information in DB")
        result = self.slack.api_call("users.list")

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
