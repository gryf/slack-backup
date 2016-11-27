#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tempfile
import os
import unittest

from slack_backup import config


CONF = """\
[common]
channels=["one","two", "three"]
database=dbfname.sqlite
quiet=1
verbose=2

[generate]
output=logs
format=text
theme=plain

[fetch]
user=someuser@address.com
password=secret
team=myteam
token=xxxx-1111111111-222222222222-333333333333-r4nd0ms7uff
"""


class TestConfig(unittest.TestCase):

    def setUp(self):

        fd, self.confname = tempfile.mkstemp()
        os.close(fd)

        with open(self.confname, 'w') as fobj:
            fobj.write(CONF)

    def tearDown(self):
        os.unlink(self.confname)

    def test_config(self):

        self.assertTrue(os.path.exists(self.confname))
        self.assertTrue(os.path.isfile(self.confname))

        args = argparse.Namespace()
        args.config = None
        args.parser = 'fetch'
        args.verbose = 2
        args.quiet = None
        args.channels = None
        args.database = None
        args.user = None
        args.password = None
        args.team = None
        args.token = None

        conf = config.Config()
        conf.update(args)
        self.assertDictEqual(vars(args), {'config': None,
                                          'parser': 'fetch',
                                          'verbose': 2,
                                          'quiet': 0,
                                          'channels': [],
                                          'database': '',
                                          'user': None,
                                          'password': None,
                                          'team': None,
                                          'token': None})

        args = argparse.Namespace()
        args.config = self.confname
        args.parser = 'fetch'
        args.verbose = 2
        args.quiet = None
        args.channels = None
        args.database = None
        args.user = None
        args.password = None
        args.team = None
        args.token = None

        conf = config.Config()
        conf.update(args)

        self.assertEqual(conf._options['verbose'], 2)
        self.assertListEqual(conf._options['channels'],
                             ['one', 'two', 'three'])
        self.assertEqual(conf._options['database'], 'dbfname.sqlite')
        self.assertEqual(conf._options['user'], 'someuser@address.com')

        self.assertDictEqual(vars(args), {'config': self.confname,
                                          'parser': 'fetch',
                                          'verbose': 2,
                                          'quiet': 0,
                                          'channels': ['one', 'two', 'three'],
                                          'database': 'dbfname.sqlite',
                                          'user': 'someuser@address.com',
                                          'password': 'secret',
                                          'team': 'myteam',
                                          'token': 'xxxx-1111111111-'
                                                   '222222222222-333333333333-'
                                                   'r4nd0ms7uff'})

        # override some conf options with commandline
        args = argparse.Namespace()
        args.config = self.confname
        args.parser = 'fetch'
        args.verbose = None
        args.quiet = 2
        args.channels = ['foo']
        args.database = None
        args.user = 'joe'
        args.password = 'ultricies'
        args.team = ''
        args.token = 'the token'

        conf = config.Config()
        conf.update(args)

        self.assertDictEqual(vars(args), {'config': self.confname,
                                          'parser': 'fetch',
                                          'verbose': 0,
                                          'quiet': 2,
                                          'channels': ['foo'],
                                          'database': 'dbfname.sqlite',
                                          'user': 'joe',
                                          'password': 'ultricies',
                                          'team': '',
                                          'token': 'the token'})
