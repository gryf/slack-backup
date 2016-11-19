#!/usr/bin/env python3
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
        channels = self._get_channel_list()
        if selected_channels:
            selected_channels = [c for c in channels
                                 if c.name in selected_channels]
        else:
            selected_channels = channels

        self._update_users()

        for channel in selected_channels:
            # history = []
            latest = 'now'

            while True:
                messages, latest = self._get_channel_history(channel, latest)
                # TODO: merge messages witihn a channel
                if not messages:
                    break

        self.session.close()

    def _get_channel_history(self, channel, latest='now'):
        result = self.slack.api_call("channels.history", channel=channel._id,
                                     count=1000, latest=latest)

        if not result.get("ok"):
            logging.error(result['error'])
            return None, None

    def _get_channel_list(self):
        result = self.slack.api_call("channels.list")

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        return [o.Channel(chan) for chan in result['channels']]

    def _update_users(self):
        """Fetch and update user list with current state in db"""
        result = self.slack.api_call("users.list", presence=0)
        all_users = self.session.query(o.User).all()

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        for user_data in result['members']:
            slackid = user_data['id']
            del user_data['id']
            idmap = self.session.query(o.IdMap).\
                    filter(o.IdMap.classname == 'User').\
                    filter(o.IdMap.slackid == slackid).one_or_none()
            if idmap:
                user = self.session.query(o.User).get(idmap.dbid)
                user.update(user_data)
            else:
                user = o.User(user_data)
                self.session.add(user)
                self.session.flush()

                idmap = o.IdMap()
                idmap.slackid = slackid
                idmap.classname = 'User'
                idmap.dbid = user.id
                self.session.add(idmap)

        self.session.commit()
