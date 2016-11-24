from unittest import TestCase
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from slack_backup import client
from slack_backup import objects as o

CHANNELS = {"ok": True,
            "channels": [{"id": "C00000000",
                          "name": "somechannel",
                          "is_channel": True,
                          "created": 1479147929,
                          "creator": "UAAAAAAAA",
                          "is_archived": False,
                          "is_general": False,
                          "is_member": True,
                          "members": ["UAAAAAAAA",
                                      "UBBBBBBBB",
                                      "UCCCCCCCC"],
                          "topic": {"value": "",
                                    "creator": "",
                                    "last_set": 0},
                          "purpose": {"value": "",
                                      "creator": "",
                                      "last_set": 0},
                          "num_members": 7},
                         {"id": "C00000001",
                          "name": "general",
                          "is_channel": True,
                          "created": 1416042849,
                          "creator": "USLACKBOT",
                          "is_archived": False,
                          "is_general": True,
                          "is_member": True,
                          "members": ["UAAAAAAAA",
                                      "UBBBBBBBB",
                                      "UCCCCCCCC"],
                          "topic": {"value": "",
                                    "creator": "",
                                    "last_set": 0},
                          "purpose": {"value": "This channel is for team-wide"
                                               " communication and "
                                               "announcements. All team "
                                               "members are in this channel.",
                                      "creator": "",
                                      "last_set": 0},
                          "num_members": 14}]}

PROFILES = [{'always_active': False,
             'api_app_id': '',
             'avatar_hash': '167c4585f3b5',
             'bot_id': 'B34RR91SQ',
             'image_1024': 'https://bla.com/2016-11-19/12345_72.png',
             'image_192': 'https://bla.com/2016-11-19/12345_72.png',
             'image_24': 'https://bla.com/2016-11-19/12345_24.png',
             'image_32': 'https://bla.com/2016-11-19/12345_32.png',
             'image_48': 'https://bla.com/2016-11-19/12345_48.png',
             'image_512': 'https://bla.com/2016-11-19/12345_72.png',
             'image_72': 'https://bla.com/2016-11-19/12345_72.png',
             'image_original': 'https://bla.com/2016-11-19/12345_original.png',
             'real_name': '',
             'real_name_normalized': '',
             'title': 'all your base are belongs to us'},
            {'avatar_hash': 'bab01f158419',
             'email': 'name1@some.mail.com',
             'first_name': 'name',
             'image_1024': 'https://bla.com/2016-11-19/23456_512.png',
             'image_192': 'https://bla.com/2016-11-19/23456_192.png',
             'image_24': 'https://bla.com/2016-11-19/23456_24.png',
             'image_32': 'https://bla.com/2016-11-19/23456_32.png',
             'image_48': 'https://bla.com/2016-11-19/23456_48.png',
             'image_512': 'https://bla.com/2016-11-19/23456_512.png',
             'image_72': 'https://bla.com/2016-11-19/23456_72.png',
             'image_original': 'https://bla.com/2016-11-19/23456_original.png',
             'last_name': 'lastname',
             'real_name': 'name lastname',
             'real_name_normalized': 'name lastname'},
            {'avatar_hash': '398907b00c64',
             'email': 'name2@@foobar.mail.net',
             'first_name': 'othername',
             'image_1024': 'https://bla.com/2016-11-19/34567_72.gif',
             'image_192': 'https://bla.com/2016-11-19/34567_72.gif',
             'image_24': 'https://bla.com/2016-11-19/34567_24.gif',
             'image_32': 'https://bla.com/2016-11-19/34567_32.gif',
             'image_48': 'https://bla.com/2016-11-19/34567_48.gif',
             'image_512': 'https://bla.com/2016-11-19/34567_72.gif',
             'image_72': 'https://bla.com/2016-11-19/34567_72.gif',
             'image_original': 'https://bla.com/2016-11-19/34567_original.gif',
             'last_name': 'totallylast',
             'phone': '',
             'real_name': 'othername totallylast',
             'real_name_normalized': 'othername totallylast',
             'skype': '',
             'title': 'blah & blah'},
            {'avatar_hash': 'sv1454671952',
             'fields': None,
             'first_name': 'slackbot',
             'image_192': 'https://bla.com/65f9/img/slackbot_192.png',
             'image_24': 'https://bla.com/181c/img/slackbot_24.png',
             'image_32': 'https://bla.com/0fac/slackbot/assets/service_32.png',
             'image_48': 'https://bla.com/4fac/slackbot/assets/service_48.png',
             'image_512': 'https://bla.com/1803/img/slackbot_512.png',
             'image_72': 'https://bla.com/1780/img/slackbot_72.png',
             'last_name': '',
             'real_name': 'slackbot',
             'real_name_normalized': 'slackbot'}]

USERS = {'cache_ts': 1479577519,
         'ok': True,
         'members': [{'color': 'd58247',
                      'deleted': False,
                      'id': 'UAAAAAAAA',
                      'is_admin': False,
                      'is_bot': True,
                      'is_owner': False,
                      'is_primary_owner': False,
                      'is_restricted': False,
                      'is_ultra_restricted': False,
                      'name': 'borg',
                      'profile': PROFILES[0],
                      'real_name': '',
                      'status': None,
                      'team_id': 'T0000TEST',
                      'tz': None,
                      'tz_label': 'Pacific Standard Time',
                      'tz_offset': -28800},
                     {'color': '4bbe2e',
                      'deleted': False,
                      'has_2fa': False,
                      'id': 'UBBBBBBBB',
                      'is_admin': True,
                      'is_bot': False,
                      'is_owner': True,
                      'is_primary_owner': False,
                      'is_restricted': False,
                      'is_ultra_restricted': False,
                      'name': 'name1',
                      'profile': PROFILES[1],
                      'real_name': 'name lastname',
                      'status': None,
                      'team_id': 'T0000TEST',
                      'tz': 'America/Los_Angeles',
                      'tz_label': 'Pacific Standard Time',
                      'tz_offset': -28800},
                     {'color': 'e96699',
                      'deleted': False,
                      'has_2fa': False,
                      'id': 'UCCCCCCCC',
                      'is_admin': False,
                      'is_bot': False,
                      'is_owner': False,
                      'is_primary_owner': False,
                      'is_restricted': False,
                      'is_ultra_restricted': False,
                      'name': 'name2',
                      'profile': PROFILES[2],
                      'real_name': 'othername totallylast',
                      'status': None,
                      'team_id': 'T0000TEST',
                      'tz': 'America/Los_Angeles',
                      'tz_label': 'Pacific Standard Time',
                      'tz_offset': -28800},
                     {'color': '757575',
                      'deleted': False,
                      'id': 'USLACKBOT',
                      'is_admin': False,
                      'is_bot': False,
                      'is_owner': False,
                      'is_primary_owner': False,
                      'is_restricted': False,
                      'is_ultra_restricted': False,
                      'name': 'slackbot',
                      'profile': PROFILES[3],
                      'real_name': 'slackbot',
                      'status': None,
                      'team_id': 'T0000TEST',
                      'tz': None,
                      'tz_label': 'Pacific Standard Time',
                      'tz_offset': -28800}]}

MSGS = {'messages': [{"type": "message",
                      "user": "UAAAAAAAA",
                      "text": "Class aptent taciti sociosqu ad litora torquent"
                              " per conubia nostra, per",
                      "ts": "1479501074.000032"},
                     {"reactions": [{"name": "+1",
                                     "users": ["UBBBBBBBB", "UCCCCCCCC"],
                                     "count": 2}],
                      "attachments": [{"service_icon": "https://bla/icon.png",
                                       "title": "Nulla sollicitudin",
                                       "thumb_width": 400,
                                       "thumb_height": 400,
                                       "from_url": "https://bla",
                                       "service_name": "Bla",
                                       "fallback": "Bla: Nulla sollicitudin",
                                       "title_link": "https://bla/nulla",
                                       "text": "Bla - bla bla",
                                       "thumb_url": "https://avatars/1.gif",
                                       "id": 1}],
                      "type": "message",
                      "user": "UCCCCCCCC",
                      "text": "Mauris ut metus sit amet mi cursus commodo. "
                              "Morbi congue mauris ac sapien. "
                              "https://bla/nulla",
                      "ts": "1479493038.000029"},
                     {"subtype": "pinned_item",
                      "item": {"mode": "hosted",
                               "size": 2949,
                               "comments_count": 1,
                               "timestamp": 1479146954,
                               "url_private_download": "https://files.slack."
                                                       "com/files-pri/bin.bin",
                               "is_external": False,
                               "external_type": "",
                               "username": "",
                               "display_as_bot": False,
                               "pinned_to": ["C00000001"],
                               "permalink_public": "https://slack-files.com/"
                                                   "hash",
                               "channels": ["C00000001"],
                               "title": "binary.prg",
                               "ims": [],
                               "url_private": "https://files.slack.com/hash/"
                                              "binary.prg",
                               "groups": [],
                               "filetype": "binary",
                               "user": "UAAAAAAAA",
                               "initial_comment": {"is_intro": True,
                                                   "user": "UAAAAAAAA",
                                                   "channel": "",
                                                   "timestamp": 1479146954,
                                                   "created": 1479146954,
                                                   "comment": "sample image",
                                                   "id": "Fc331R6CNT"},
                               "permalink": "https://bla.slack.com/files/borg/"
                                            "F331R60LX/binary.prg",
                               "name": "Conan.hires.prg",
                               "num_stars": 1,
                               "public_url_shared": False,
                               "is_public": True,
                               "mimetype": "application/octet-stream",
                               "created": 1479146954,
                               "id": "F331R60LX",
                               "pretty_type": "Binary",
                               "editable": False},
                      "item_type": "F",
                      "type": "message",
                      "user": "UAAAAAAAA",
                      "text": "<@UAAAAAAAA|borg> pinned their Binary "
                              "<https://bla.slack.com/files/borg/F331R60LX/"
                              "binary.prg|Binary.prg> to this channel.",
                      "ts": "1479146975.000197"},
                     {"type": "message",
                      "subtype": "channel_join",
                      "user": "UAAAAAAAA",
                      "text": "<@UAAAAAAAA|borg> has joined the channel",
                      "ts": "1479108214.000002"},
                     {"display_as_bot": False,
                      "subtype": "file_share",
                      "username": "<@UCCCCCCCC|name2>",
                      "file": {"thumb_960": "https://files.slack.com/files-tmb"
                                            "/hash/screenshot_960.png",
                               "user": "UCCCCCCCC",
                               "size": 77222,
                               "thumb_1024_h": 754,
                               "timestamp": 1479407569,
                               "url_private_download": "https://files.slack.co"
                                                       "m/files-pri/hsh/downlo"
                                                       "ad/screenshot.png",
                               "thumb_360": "https://files.slack.com/files-tmb"
                                            "/hash/screenshot_360.png",
                               "username": "",
                               "external_type": "",
                               "thumb_64": "https://files.slack.com/files-tmb/"
                                           "hash/screenshot_64.png",
                               "created": 1479407569,
                               "ims": [],
                               "groups": [],
                               "filetype": "png",
                               "thumb_1024": "https://files.slack.com/files-"
                                             "tmb/hash/screenshot_1024.png",
                               "original_w": 1193,
                               "name": "Screenshot.png",
                               "thumb_360_h": 265,
                               "is_public": True,
                               "thumb_960_h": 707,
                               "original_h": 878,
                               "mimetype": "image/png",
                               "id": "F3405RRB5",
                               "pretty_type": "PNG",
                               "editable": False,
                               "thumb_960_w": 960,
                               "thumb_80": "https://files.slack.com/files-tmb/"
                                           "hash/screenshot_80.png",
                               "comments_count": 0,
                               "image_exif_rotation": 1,
                               "thumb_160": "https://files.slack.com/files-tmb"
                                            "/hash/screenshot_160.png",
                               "thumb_480_w": 480,
                               "is_external": False,
                               "display_as_bot": False,
                               "thumb_720_h": 530,
                               "channels": ["C00000001"],
                               "title": "Screenshot.png",
                               "thumb_480": "https://files.slack.com/files-tmb"
                                            "/hash/screenshot_480.png",
                               "url_private": "https://files.slack.com/files-"
                                              "pri/hsh/screenshot.png",
                               "mode": "hosted",
                               "thumb_1024_w": 1024,
                               "permalink": "https://esm64.slack.com/files/"
                                            "name2/F3405RRB5/screenshot.png",
                               "thumb_480_h": 353,
                               "public_url_shared": False,
                               "thumb_720": "https://files.slack.com/files-tmb"
                                            "/hash/screenshot_720.png",
                               "thumb_360_w": 360,
                               "permalink_public": "https://slack-files.com/"
                                                   "hsh-7dbb96b758",
                               "thumb_720_w": 720},
                      "type": "message",
                      "user": "UCCCCCCCC",
                      "bot_id": None,
                      "text": "<@UCCCCCCCC|name2> uploaded a file: "
                              "<https://esm64.slack.com/files/name2/F3405RRB5/"
                              "screenshot.png|Screenshot.png>",
                      "ts": "1478107371.000052",
                      "upload": True}],
        "ok": True,
        "latest": "1479501075.000020",
        "has_more": True}

MSG2 = {'messages': [{"type": "message",
                      "user": "UCCCCCCCC",
                      "text": "Pellentesque molestie nunc id enim. Etiam "
                              "mollis tempus neque. Duis. per conubia "
                              "nostra, per",
                      "ts": "1479505026.000002"}],
        "ok": True,
        "latest": "1479505026.000003",
        "has_more": True}

MSG3 = {"ok": True,
        "oldest": "1479505026.000003",
        "messages": [],
        "has_more": False,
        "is_limited": False}


class FakeArgs(object):
    token = 'token_string'
    user = 'fake_user'
    password = 'fake_password'
    team = 'fake_team'
    database = None
    channels = None
    assets = 'assets'


class TestApiCalls(TestCase):

    def test_channels_list(self):
        cl = client.Client(FakeArgs())
        cl.slack.api_call = MagicMock(return_value=CHANNELS)
        channels = cl._channels_list()
        self.assertListEqual(CHANNELS['channels'], channels)

    def test_users_list(self):
        cl = client.Client(FakeArgs())
        cl.slack.api_call = MagicMock(return_value=USERS)
        users = cl._users_list()
        self.assertListEqual(USERS['members'], users)

    def test_channels_history(self):
        cl = client.Client(FakeArgs())

        cl.slack.api_call = MagicMock(return_value=USERS)
        cl.update_users()

        cl.slack.api_call = MagicMock(return_value=CHANNELS)
        cl.update_channels()

        cl.slack.api_call = MagicMock()
        cl.slack.api_call.side_effect = [MSGS, MSG2, MSG3]

        channel = cl.q(o.Channel).filter(o.Channel.slackid ==
                                         "C00000001").one()

        msg, ts = cl._channels_history(channel, 0)
        self.assertEqual(len(msg), 5)
        self.assertEqual(ts, '1479501074.000032')

        msg, ts = cl._channels_history(channel, ts)
        self.assertEqual(len(msg), 1)
        self.assertEqual(ts, '1479505026.000002')

        msg, ts = cl._channels_history(channel, ts)
        self.assertEqual(len(msg), 0)
        self.assertIsNone(ts)


class TestClient(TestCase):

    def test_update_users(self):
        cl = client.Client(FakeArgs())
        cl.slack.api_call = MagicMock(return_value=USERS)
        cl.update_users()
        users = cl.session.query(o.User).all()
        self.assertEqual(len(users), 4)
        self.assertEqual(users[0].id, 1)

        cl.update_users()
        users = cl.session.query(o.User).all()
        self.assertEqual(len(users), 4)
        self.assertEqual(users[0].id, 1)
        self.assertEqual(users[0].slackid, 'UAAAAAAAA')


class TestMessage(TestCase):

    def setUp(self):
        args = FakeArgs()
        args.channels = ['general']

        self.cl = client.Client(args)
        self.cl.downloader.authorize = MagicMock()
        self.cl.slack.api_call = MagicMock(return_value=USERS)
        self.cl.update_users()

        self.cl.slack.api_call = MagicMock(return_value=CHANNELS)
        self.cl.update_channels()

        self.cl.slack.api_call = MagicMock()

    def test_update_history(self):

        self.cl.slack.api_call.side_effect = [MSGS, MSG3]
        self.cl.update_history()
        self.assertEqual(len(self.cl.q(o.Message).all()), 5)

        self.cl.slack.api_call.side_effect = [MSG2, MSG3]
        self.cl.update_history()

        self.assertEqual(len(self.cl.q(o.Message).all()), 6)
