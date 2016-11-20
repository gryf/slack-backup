import unittest

from slack_backup import db
from slack_backup import objects as o


class TestMapping(unittest.TestCase):

    def test_users(self):
        db.connect()
        session = db.Session()

        users = session.query(o.User).all()
        self.assertListEqual(users, [])

        session.add(o.User())

        users = session.query(o.User).all()
        self.assertEqual(len(users), 1)

        user = users[0]

        self.assertListEqual(user.channels, [])
        self.assertListEqual(user.topics, [])
        self.assertListEqual(user.purposes, [])
        self.assertEqual(user.id, 1)
