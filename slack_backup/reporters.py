"""
Reporters module.

There are several classes for specific format reporting, and also some of the
slack conversation/convention parsers.
"""
import os
import logging

from slack_backup import objects as o


class Reporter(object):
    """Base reporter class"""
    ext = ''

    def __init__(self, args, query):
        self.out = args.output
        self.q = query

        self.channels = self._get_channels(args.channels)

    def _get_channels(self, selected_channels):
        """
        Retrive channels from db and return those which names matched from
        selected_channels list
        """
        result = []
        all_channels = self.q(o.Channel).all()
        if not selected_channels:
            return all_channels

        for channel in all_channels:
            if channel.name in selected_channels:
                result.append(channel)

        return channel

    def generate(self):
        """Generate raport it's a dummmy one - for use with none reporter"""
        return

    def get_log_path(self, name):
        """Return relative log file name """
        return os.path.join(self.out, name + self.ext)

    def write_msg(self, message, log):
        """Write message to file"""
        raise NotImplementedError()


class TextReporter(Reporter):
    """Text aka IRC reporter"""
    ext = '.log'

    def generate(self):
        """Generate raport"""
        for channel in self.channels:
            log_path = self.get_log_path(channel.name)
            for message in self.q(o.Message).\
                    filter(o.Message.channel == channel).\
                    order_by(o.Message.ts).all():
                self.write_msg(message, log_path)

    def write_msg(self, message, log):
        """Write message to file"""


def get_reporter(args, query):
    """Return object of right reporter class"""
    reporters = {'text': TextReporter}

    klass = reporters.get(args.format, Reporter)
    if klass.__name__ == 'Reporter':
        logging.warning('None, or wrong (%s) formatter selected, falling to'
                        ' None Reporter', args.format)
    return klass(args, query)
