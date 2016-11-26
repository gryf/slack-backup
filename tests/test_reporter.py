from unittest import TestCase
from unittest.mock import MagicMock

from slack_backup import reporters as r


class FakeUser(object):
    def __init__(self, slackid, name):
        self.slackid = slackid
        self.name = name


class TestReporter(TestCase):

    def setUp(self):

        users = [FakeUser('U111AAAAA', 'user1'),
                 FakeUser('U111BBBBB', 'user2'),
                 FakeUser('U111CCCCC', 'funky_username1'),
                 FakeUser('U111DDDDD', 'user-name°')]

        args = MagicMock()
        args.output = 'logs'
        query1 = MagicMock()
        query1.all = MagicMock(return_value=users)
        query = MagicMock(return_value=query1)

        self.reporter = r.TextReporter(args, query)

    def test_regexp(self):
        text = 'Cras vestibulum <@U111AAAAA|user1> erat ultrices neque.'
        self.assertEqual(self.reporter._filter_slackid(text),
                         'Cras vestibulum user1 erat ultrices neque.')

        text = ('Cras vestibulum <@U111AAAAA|user1> erat ultrices '
                '<@U111AAAAA|user1> neque.')
        self.assertEqual(self.reporter._filter_slackid(text),
                         'Cras vestibulum user1 erat ultrices user1 neque.')

        text = ('<@U111BBBBB|user2>Praesent vel enim sed eros luctus '
                'imperdiet.\nMauris neque ante, <@U111DDDDD> placerat at, '
                'mollis vitae, faucibus quis, <@U111CCCCC>leo. Ut feugiat.')
