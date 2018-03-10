import unittest
from unittest import mock

from slack_backup import reporters


class FakeUser(object):
    def __init__(self, slackid, name):
        self.slackid = slackid
        self.name = name


class TestReporter(unittest.TestCase):

    def setUp(self):

        args = mock.MagicMock()
        args.output = 'logs'

        self.one = mock.MagicMock()
        query2 = mock.MagicMock()
        query2.one = self.one
        query1 = mock.MagicMock()
        query1.filter = mock.MagicMock(return_value=query2)
        query = mock.MagicMock(return_value=query1)

        self.reporter = reporters.TextReporter(args, query)

    def test_regexp1(self):
        self.one.return_value = FakeUser('U111AAAAA', 'user1')
        text = 'Cras vestibulum <@U111AAAAA|user1> erat ultrices neque.'

        self.assertEqual(self.reporter._filter_slackid(text),
                         'Cras vestibulum user1 erat ultrices neque.')

    def test_regexp2(self):
        self.one.side_effect = [FakeUser('U111AAAAA', 'user1'),
                                FakeUser('U111AAAAA', 'user1')]
        text = ('Cras vestibulum <@U111AAAAA|user1> erat ultrices '
                '<@U111AAAAA|user1> neque.')
        self.assertEqual(self.reporter._filter_slackid(text),
                         'Cras vestibulum user1 erat ultrices user1 neque.')

    def test_regexp3(self):
        self.one.side_effect = [FakeUser('U111BBBBB', 'user2'),
                                FakeUser('U111DDDDD', 'user-name°'),
                                FakeUser('U111CCCCC', 'funky_username1')]
        text = ('<@U111BBBBB|user2> Praesent vel enim sed eros luctus '
                'imperdiet.\nMauris neque ante, <@U111DDDDD> placerat at, '
                'mollis vitae, faucibus quis, <@U111CCCCC> leo. Ut feugiat.')
        self.assertEqual(self.reporter._filter_slackid(text),
                         'user2 Praesent vel enim sed eros luctus '
                         'imperdiet.\nMauris neque ante, user-name° placerat '
                         'at, mollis vitae, faucibus quis, funky_username1 '
                         'leo. Ut feugiat.')
