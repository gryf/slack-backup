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
    symbols = {'plain': {'join': '->',
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

        self.emoji = emoji.EMOJI.get(args.theme, {})

        self.channels = self._get_channels(args.channels)
        self.users = self.q(o.User).all()

    def generate(self):
        """Generate raport for each channel"""
        for channel in self.channels:
            messages = []
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
                messages.append(message)
            self.write_msg(messages, log_path)

    def get_log_path(self, name):
        """Return relative log file name """
        return os.path.join(self.out, name + self.ext)

    def write_msg(self, messages, log):
        """Write message to file"""
        with open(log, "a") as fobj:
            for message in messages:
                data = self._process_message(message)
                fobj.write(data['tpl'].format(**data))

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
        return result

    def _process_message(self, msg):
        """
        Make changes to the text (replace slack ids, replace representation of
        urls, substitute images etc) and return dict with data suitable to
        display.
        """
        processor = self.types.get(msg.type, self._msg)
        data = processor(msg)
        data.update({'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                'tpl': "{date} {nick} {msg}"})

        return data

    def _msg_join(self, msg):
        """return data for join"""
        return {'msg': msg.text,
                'nick': self._get_symbol('join')}

    def _msg_leave(self, msg):
        """return data for leave"""
        return {'msg': msg.text,
                'nick': self._get_symbol('leave')}

    def _msg_topic(self, msg):
        """return data for set topic"""
        return {'msg': msg.text,
                'nick': self._get_symbol('topic')}

    def _msg_me(self, msg):
        """return data for /me"""
        return {'msg': msg.text,
                'nick': self._get_symbol('me')}

    def _msg_file(self, msg):
        """return data for file"""
        return {'msg': msg.text,
                'nick': self._get_symbol('file')}

    def _msg(self, msg):
        """return data for all other message types"""
        return {'msg': msg.text,
                'nick': msg.user.name}

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


class NoneReporter(Reporter):
    """Dummy reporter used for fallback"""

    def generate(self):
        """Generate raport it's a dummmy one - for use with none reporter"""
        return


class TextReporter(Reporter):
    """Text aka IRC reporter"""
    ext = '.log'
    tpl = '{date} {nick:>{max_len}} {separator} {msg}\n'

    def __init__(self, args, query):
        super(TextReporter, self).__init__(args, query)
        utils.makedirs(self.out)
        self._max_len = 0

    def generate(self):
        """Generate raport"""
        for channel in self.channels:
            messages = []
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
                messages.append(message)

            self.write_msg(messages, log_path)

    def _set_max_len(self, channel):
        """calculate max_len for sepcified channel"""
        users = [m.user for m in channel.messages]
        users = set([u.name for u in users])

        self._max_len = 0
        for user_name in users:
            if len(user_name) > self._max_len:
                self._max_len = len(user_name)

    def _process_message(self, msg):
        """
        Check what kind of message we are dealing with and do appropriate
        formatting
        """
        data = super(TextReporter, self)._process_message(msg)
        data['msg'] = self._filter_slackid(data['msg'])
        data['msg'] = self._fix_newlines(data['msg'])
        data['msg'] = self._remove_entities(data['msg'])
        data.update({'date': msg.datetime().strftime("%Y-%m-%d %H:%M:%S"),
                     'max_len': self._max_len,
                     'separator': self._get_symbol('separator'),
                     'tpl': self.tpl})
        return data

    def _msg_file(self, msg):
        """return data for file"""
        fpath = os.path.abspath(msg.file.filepath)
        return {'msg': self.url_pat.sub('(file://' + fpath + ') ' +
                                        msg.file.title, msg.text),
                'nick': self._get_symbol('file')}

    def _msg(self, msg):
        """return data for all other message types"""

        data = super(TextReporter, self)._msg(msg)
        result = ''

        if msg.attachments:
            for att in msg.attachments:
                if att.title:
                    att_text = att.title + '\n'
                else:
                    att_text = self._fix_newlines(att.fallback) + '\n'

                if att.text:
                    att_text += att.text

                result += att_text + '\n'

        data['msg'] += result.strip()
        return data

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

    klass = reporters.get(args.format, NoneReporter)
    if klass.__name__ == 'Reporter':
        logging.warning('None, or wrong (%s) formatter selected, falling to'
                        ' None Reporter', args.format)
    return klass(args, query)
