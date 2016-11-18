#!/usr/bin/env python3
"""
Create backup for certain date for specified channel in slack
"""
import argparse
import logging

import slackclient

from slack_backup import objects


class Client(object):
    def __init__(self, token):
        self.slack = slackclient.SlackClient(token)

    def get_hisotry(self, selected_channels=None, from_date=0):
        channels = self._get_channel_list()
        if selected_channels:
            selected_channels = [c for c in channels
                                 if c.name in selected_channels]
        else:
            selected_channels = channels

        users = self._get_user_list()

        for channel in selected_channels:
            history = []
            latest = 'now'

            while True:
                messages, latest = self._get_channel_history(channel, latest)
                # TODO: merge messages witihn a channel
                if not messages:
                    break

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

        return [objects.Channel(chan) for chan in result['channels']]

    def _get_user_list(self):
        result = self.slack.api_call("users.list", presence=0)

        if not result.get("ok"):
            logging.error(result['error'])
            return None

        return [objects.User(user) for user in result['members']]
