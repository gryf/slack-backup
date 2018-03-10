"""
Reporters module.

There are several classes for specific format reporting, and also some of the
slack conversation/convention parsers.
"""
import os
import errno
import html.parser
import logging
import re

from slack_backup import objects as o
from slack_backup import utils
from slack_backup import emoji


class Reporter(object):
    """Base reporter class"""
    ext = ''
    url_pat = re.compile(r'(?P<replace><http[^>]+>)')
    slackid_pat = re.compile(r'(?P<replace><@'
                             '(?P<slackid>U[A-Z,0-9]+)(\|[^>]+)?[^>]*>)')

    def __init__(self, args, query):
        self.out = args.output
        self.theme = args.theme
        self.q = query
        self.types = {"channel_join": self._msg_join,
                      "channel_leave": self._msg_leave,
                      "channel_topic": self._msg_topic,
                      "file_share": self._msg_file,
                      "me_message": self._msg_me}
        self.symbols = {'plain': {'join': '->',
                                  'leave': '<-',
                                  'me': '*',
                                  'file': '-',
                                  'topic': '+',
                                  'separator': '|'},
                        'unicode': {'join': '⮊',
                                    'leave': '⮈',
                                    'me': '🟊',
                                    'file': '📂',
                                    'topic': '🟅',
                                    'separator': '│'}}
        self.emoji = emoji.EMOJI.get(args.theme, {})

        self.channels = self._get_channels(args.channels)
        self.users = self.q(o.User).all()

    def generate(self):
        """Generate raport it's a dummmy one - for use with none reporter"""
        return

    def get_log_path(self, name):
        """Return relative log file name """
        return os.path.join(self.out, name + self.ext)

    def write_msg(self, message, log):
        """Write message to file"""
        raise NotImplementedError()

    def _get_symbol(self, item):
        """Return appropriate item depending on the selected theme"""
        return self.symbols[self.theme][item]

    def _get_channels(self, selected_channels):
        """
        Retrieve channels from db and return those which names matched from
        selected_channels list
        """
        all_channels = self.q(o.Channel).all()
        if not selected_channels:
            return all_channels

        result = []
        for channel in all_channels:
            if channel.name in selected_channels:
                result.append(channel)

    def _msg_join(self, msg, text):
        """return formatter for join"""
        return

    def _msg_leave(self, msg, text):
        """return formatter for leave"""
        return

    def _msg_topic(self, msg, text):
        """return formatter for set topic"""
        return

    def _msg_me(self, msg, text):
        """return formatter for /me"""
        return

    def _msg_file(self, msg, text):
        """return formatter for /me"""
        return

    def _filter_slackid(self, text):
        """filter out all of the id from slack"""
        match = True
        while match:
            match = self.slackid_pat.search(text)
            if not match:
                return text

            match = match.groupdict()
            user = self.q(o.User).filter(o.User.slackid ==
                                         match['slackid']).one()
            text = text.replace(match['replace'], user.name)

        return text


class TextReporter(Reporter):
    """Text aka IRC reporter"""
    ext = '.log'

    def __init__(self, args, query):
        super(TextReporter, self).__init__(args, query)
        utils.makedirs(self.out)
        self._max_len = 0

        return

    def generate(self):
        """Generate raport"""
        for channel in self.channels:
            log_path = self.get_log_path(channel.name)
            self._set_max_len(channel)
            try:
                os.unlink(log_path)
            except IOError as err:
                if err.errno != errno.ENOENT:
                    raise
            for message in self.q(o.Message).\
                    filter(o.Message.channel == channel).\
                    order_by(o.Message.ts).all():
                self.write_msg(message, log_path)

    def write_msg(self, message, log):
        """Write message to file"""
        with open(log, "a") as fobj:
            fobj.write(self._format_message(message))

    def _set_max_len(self, channel):
        """calculate max_len for sepcified channel"""
        users = [m.user for m in channel.messages]
        users = set([u.name for u in users])

        self._max_len = 0
        for user_name in users:
            if len(user_name) > self._max_len:
                self._max_len = len(user_name)

    def _format_message(self, msg):
        """
        Check what kind of message we are dealing with and do appropriate
        formatting
        """
        msg_txt = self._filter_slackid(msg.text)
        msg_txt = self._fix_newlines(msg_txt)
        for emoticon in self.emoji:
            msg_txt = msg_txt.replace(emoticon, self.emoji[emoticon])
        formatter = self.types.get(msg.type, self._msg)

        return formatter(msg, msg_txt)

    def _msg_join(self, msg, text):
        """return formatter for join"""
        data = {'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                'msg': text,
                'max_len': self._max_len,
                'separator': self._get_symbol('separator'),
                'nick': self._get_symbol('join')}
        return '{date} {nick:>{max_len}} {separator} {msg}\n'.format(**data)

    def _msg_leave(self, msg, text):
        """return formatter for leave"""
        data = {'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                'msg': text,
                'max_len': self._max_len,
                'separator': self._get_symbol('separator'),
                'nick': self._get_symbol('leave')}
        return '{date} {nick:>{max_len}} {separator} {msg}\n'.format(**data)

    def _msg_topic(self, msg, text):
        """return formatter for set topic"""
        data = {'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                'msg': text,
                'max_len': self._max_len,
                'separator': self._get_symbol('separator'),
                'char': self._get_symbol('topic')}
        return '{date} {char:>{max_len}} {separator} {msg}\n'.format(**data)

    def _msg_me(self, msg, text):
        """return formatter for /me"""
        data = {'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                'msg': text,
                'max_len': self._max_len,
                'nick': msg.user.name,
                'separator': self._get_symbol('separator'),
                'char': self._get_symbol('me')}
        return '{date} {char:>{max_len}} {separator} {nick} {msg}\n'.\
            format(**data)

    def _msg_file(self, msg, text):
        """return formatter for file"""
        fpath = os.path.abspath(msg.file.filepath)


        data = {'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                'msg': self.url_pat.sub('(file://' + fpath + ') ' +
                                        msg.file.title, text),
                'max_len': self._max_len,
                'separator': self._get_symbol('separator'),
                'filename': fpath,
                'nick': msg.user.name,
                'char': self._get_symbol('file')}
        return ('{date} {char:>{max_len}} {separator} {nick} '
                'shared file "{filename}"{msg}\n'.format(**data))

    def _msg(self, msg, text):
        """return formatter for all other message types"""

        data = {'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                'msg': text,
                'max_len': self._max_len,
                'separator': self._get_symbol('separator'),
                'nick': msg.user.name}
        result = '{date} {nick:>{max_len}} {separator} {msg}\n'.format(**data)

        if msg.attachments:
            for att in msg.attachments:
                if att.title:
                    att_text = "\n" + att.title + '\n'
                else:
                    att_text = "\n" + self._fix_newlines(att.fallback) + '\n'

                if att.text:
                    att_text += att.text

                att_text = self._fix_newlines(att_text)
                # remove first newline
                att_text = att_text[1:]

                result += att_text + '\n'

        return result

    def _remove_entities(self, text):
        """replace html entites into appropriate chars"""
        return html.parser.HTMLParser().unescape(text)


    def _fix_newlines(self, text):
        """Shift text with new lines to the right with separator"""
        shift = 19  # length of the date
        shift += 1  # separator space
        shift += self._max_len  # length reserved for the nicks
        shift += 1  # separator space
        return text.replace('\n', '\n' + shift * ' ' +
                            self._get_symbol('separator') + ' ')


def get_reporter(args, query):
    """Return object of right reporter class"""
    reporters = {'text': TextReporter}

    klass = reporters.get(args.format, Reporter)
    if klass.__name__ == 'Reporter':
        logging.warning('None, or wrong (%s) formatter selected, falling to'
                        ' None Reporter', args.format)
    return klass(args, query)
