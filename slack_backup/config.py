#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration module for slack-backup
"""
import json
import os
import configparser


class Config(object):
    """Configuration keeper"""

    ints = ['verbose', 'quiet']
    bools = ['url_file_to_attachment']

    sections = {'common': ['channels', 'database', 'quiet', 'verbose'],
                'fetch': ['user', 'password', 'team', 'token',
                          'url_file_to_attachment', 'raw_dir'],
                'generate': ['output', 'format', 'theme']}

    def __init__(self):
        """
        Init. Read config, if exists, and update passed argument parser
        object.
        """

        self.cp = configparser.ConfigParser()
        self._options = {'channels': [],
                         'database': None,
                         'quiet': 0,
                         'verbose': 0,
                         'user': None,
                         'password': None,
                         'team': None,
                         'token': None,
                         'output': None,
                         'format': None,
                         'theme': None,
                         'url_file_to_attachment': False,
                         'raw_dir': None}
        # This message supposed to be displayed in INFO level. During the time
        # of running the code where it should be displayed there is no
        # complete information about logging level. Displaying message is
        # dependent on the a) config file, b) argument from commandline. Let's
        # resolve if user want to have that information or not after merging
        # those two sources. If user do not want to see any message in INFO
        # level, we shouldn't do so.
        self.msg = ''

    def update(self, args):
        self.load_config(args)
        self.parse_loaded_options()
        self.update_args(args)
        return self.msg

    def load_config(self, args):

        path = ''
        if hasattr(args, 'config') and args.config:
            path = args.config

        locations = [path,
                     './slack-backup.ini',
                     os.path.expandvars('$XDG_CONFIG_HOME/slack-backup.ini'),
                     os.path.expandvars('$HOME/.config/slack-backup.ini')]

        for location in locations:
            if os.path.exists(location):
                self.cp.read(location)
                self.msg = 'Found configuration file: %s' % location
                break
        else:
            self.msg = 'No configuration file found'

    def parse_loaded_options(self):

        for section in self.cp.sections():
            if section not in self.sections:
                continue

            for option in self.sections[section]:
                if option in self.ints:
                    val = self.cp.getint(section, option, fallback=0)
                elif option in self.bools:
                    val = self.cp.getboolean(section, option, fallback=False)
                elif option == 'channels':
                    val = self.cp.get(section, option, fallback='[]')
                    val = json.loads(val)
                else:
                    val = self.cp.get(section, option, fallback=None)

                self._options[option] = val

    def update_args(self, args):
        if 'parser' not in args:
            # it doesn't make sense to update args, since no action was
            # choosen
            return

        # special case, re-set information for verbose/quiet options
        if 'verbose' in args and args.verbose is not None:
            self._options['verbose'] = args.verbose
            if self._options['quiet'] is not None:
                self._options['quiet'] = 0
        if 'quiet' in args and args.quiet is not None:
            self._options['quiet'] = args.quiet
            if self._options['verbose'] is not None:
                self._options['verbose'] = 0

        for sec_id in (args.parser, 'common'):
            for option in self.sections[sec_id]:
                if option in args:
                    if getattr(args, option) is not None:
                        continue

                setattr(args, option, self._options[option])
