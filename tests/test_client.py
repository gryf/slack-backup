import copy
import unittest
from unittest import mock

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
                      "upload": True},
                     {'type': 'something else',
                      'ts': '1502003415232.000001',
                      "wibblr": True}],
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

STARRED = {"ok": True,
           "oldest": "1479505026.000003",
           "messages": [],
           "has_more": False,
           "is_limited": False}

SHARED = {"type": "message",
          "subtype": "file_share",
          "text": "<@UAAAAAAAA> shared a file: <https://bla."
          "slack.com/files/name%20lastname/F7ARMB4JU/17|"
          "some_spreadsheet>",
          "file": {
                   "id": "F6ABMB0Ja",
                   "created": 1479147929,
                   "timestamp": 1479147929,
                   "name": "att name",
                   "title": "some_spreadsheet",
                   "mimetype": "application/vnd.google-apps."
                   "spreadsheet",
                   "filetype": "gsheet",
                   "pretty_type": "GDocs Spreadsheet",
                   "user":  'UAAAAAAAA',
                   "editable": False,
                   "size": 666,
                   "mode": "external",
                   "is_external": True,
                   "external_type": "gdrive",
                   "is_public": True,
                   "public_url_shared": False,
                   "display_as_bot": False,
                   "username": "",
                   "url_private": "https://docs.google.com/"
                   "spreadsheets/d/name%20lastname/"
                   "edit?usp=drivesdk",
                   # removed useless thumb_* definition
                   "image_exif_rotation": 1,
                   "original_w": 1024,
                   "original_h": 1449,
                   "permalink": "https://bla.slack.com/files/"
                   "name%20lastname/F7ARMB4JU/17",
                   "channels": ["C00000001"],
                   "groups": [],
                   "ims": [],
                   "comments_count": 0,
                   "has_rich_preview": True
                  },
          "user": 'UAAAAAAAA',
          "upload": False,
          "display_as_bot": False,
          "username": "name lastname",
          "bot_id": None,
          "ts": "1479147929.000043"}

PINNED = {'attachments': [{'fallback': 'blah',
                           'id': 1,
                           'image_bytes': 5,
                           'image_height': 2,
                           'image_url': 'http://fake.com/i.png',
                           'image_width': 1,
                           'original_url': 'http://fake.com/fake',
                           'service_icon': 'http://fake.com/favicon.ico',
                           'service_name': 'fake service',
                           'text': 'the text',
                           'title': 'Fake service title',
                           'title_link': 'http://fake.com/fake'}],
          'item_type': 'C',
          'subtype': 'pinned_item',
          'text': '<@UAAAAAAAA> pinned a message to this channel.',
          'ts': '1479147929.000043',
          'type': 'message',
          'user': 'UAAAAAAAA'}

EXTERNAL_DATA = {"bot_id": None,
                 "display_as_bot": False,
                 "file": {
                          "channels": [
                                       "xxx"
                                      ],
                          "id": "F7ARMB4JU",
                          "created": 1506819447,
                          "timestamp": 1506819447,
                          "name": "17",
                          "title": "PT Card Count 9/30/17",
                          "mimetype": "application/"
                                      "vnd.google-apps.spreadsheet",
                          "filetype": "gsheet",
                          "pretty_type": "GDocs Spreadsheet",
                          "user": "xxx",
                          "editable": False,
                          "size": 37583,
                          "mode": "external",
                          "is_external": True,
                          "external_type": "gdrive",
                          "is_public": True,
                          "public_url_shared": False,
                          "display_as_bot": False,
                          "username": "",
                          "url_private": "https://docs.google.com/"
                                         "spreadsheets/d/xxx/edit?"
                                         "usp=drivesdk",
                          "thumb_64": "https://files.slack.com/files-tmb/"
                                      "xxx-F7ARMB4JU-xxx/17_64.png",
                          "thumb_80": "https://files.slack.com/files-tmb/"
                                      "xxx-F7ARMB4JU-xxx/17_80.png",
                          "thumb_360": "https://files.slack.com/files-tmb"
                                       "/xxx-F7ARMB4JU-xxx/17_360.png",
                          "thumb_360_w": 254,
                          "thumb_360_h": 360,
                          "thumb_480": "https://files.slack.com/files-tmb"
                                       "/xxx-F7ARMB4JU-xxx/17_480.png",
                          "thumb_480_w": 339,
                          "thumb_480_h": 480,
                          "thumb_160": "https://files.slack.com/files-tmb"
                                       "/xxx-F7ARMB4JU-xxx/17_160.png",
                          "thumb_720": "https://files.slack.com/files-tmb"
                                       "/xxx-F7ARMB4JU-xxx/17_720.png",
                          "thumb_720_w": 509,
                          "thumb_720_h": 720,
                          "thumb_800": "https://files.slack.com/files-tmb"
                                       "/xxx-F7ARMB4JU-xxx/17_800.png",
                          "thumb_800_w": 800,
                          "thumb_800_h": 1132,
                          "thumb_960": "https://files.slack.com/files-tmb"
                                       "/xxx-F7ARMB4JU-xxx/17_960.png",
                          "thumb_960_w": 678,
                          "thumb_960_h": 960,
                          "thumb_1024": "https://files.slack.com/files-tmb"
                                        "/xxx-F7ARMB4JU-xxx/17_1024.png",
                          "thumb_1024_w": 724,
                          "thumb_1024_h": 1024,
                          "image_exif_rotation": 1,
                          "original_w": 1024,
                          "original_h": 1449,
                          "permalink": "https://xxx.slack.com/files/xxx/"
                                       "F7ARMB4JU/17",
                          "groups": [],
                          "ims": [],
                          "comments_count": 0,
                          "has_rich_preview": True},
                 "user": "xxx",
                 "upload": False,
                 "username": "xxx"}

INTERNAL_DATA = {"bot_id": None,
                 "display_as_bot": False,
                 "file": {"channels": ["zzz"],
                          "comments_count": 1,
                          "created": 1524724681,
                          "display_as_bot": False,
                          "editable": False,
                          "external_type": "",
                          "filetype": "jpg",
                          "groups": [],
                          "id": "id",
                          "image_exif_rotation": 1,
                          "ims": [],
                          "initial_comment": {"comment": "bla",
                                              "created": 1524724681,
                                              "id": "yyy",
                                              "is_intro": True,
                                              "timestamp": 1524724681,
                                              "user": "UAAAAAAAA"},
                          "is_external": False,
                          "is_public": True,
                          "mimetype": "image/jpeg",
                          "mode": "hosted",
                          "name": "img.jpg",
                          "original_h": 768,
                          "original_w": 1080,
                          "permalink": "https://fake.slack.com/files/"
                                       "UAAAAAAAA/id/img.jpg",
                          "permalink_public": "https://slack-files.com/"
                                              "TXXXXXX-id-3de9b969d2",
                          "pretty_type": "JPEG",
                          "public_url_shared": False,
                          "reactions": [{"count": 1,
                                         "name": "thinking_face",
                                         "users": ["U6P9KEALW"]}],
                          "size": 491335,
                          "thumb_1024": "https://files.slack.com/files-tmb/"
                                        "TXXXXXX-id-123/img_1024.jpg",
                          "thumb_1024_h": 728,
                          "thumb_1024_w": 1024,
                          "thumb_160": "https://files.slack.com/files-tmb/"
                                       "TXXXXXX-id-123/img_160.jpg",
                          "thumb_360": "https://files.slack.com/files-tmb/"
                                       "TXXXXXX-id-123/img_360.jpg",
                          "thumb_360_h": 256,
                          "thumb_360_w": 360,
                          "thumb_480": "https://files.slack.com/files-tmb/"
                                       "TXXXXXX-id-123/img_480.jpg",
                          "thumb_480_h": 341,
                          "thumb_480_w": 480,
                          "thumb_64": "https://files.slack.com/files-tmb/"
                                      "TXXXXXX-id-123/img_64.jpg",
                          "thumb_720": "https://files.slack.com/files-tmb/"
                                       "TXXXXXX-id-123/img_720.jpg",
                          "thumb_720_h": 512,
                          "thumb_720_w": 720,
                          "thumb_80": "https://files.slack.com/files-tmb/"
                                      "TXXXXXX-id-123/img_80.jpg",
                          "thumb_800": "https://files.slack.com/files-tmb/"
                                       "TXXXXXX-id-123/img_800.jpg",
                          "thumb_800_h": 569,
                          "thumb_800_w": 800,
                          "thumb_960": "https://files.slack.com/files-tmb/"
                                       "TXXXXXX-id-123/img_960.jpg",
                          "thumb_960_h": 683,
                          "thumb_960_w": 960,
                          "timestamp": 1524724681,
                          "title": "img.jpg",
                          "url_private": "https://files.slack.com/files-pri/"
                                         "TXXXXXX-id/img.jpg",
                          "url_private_download": "https://files.slack.com/"
                                                  "files-pri/TXXXXXX-id/"
                                                  "download/img.jpg",
                          "user": "UAAAAAAAA",
                          "username": ""},
                 "subtype": "file_share",
                 "text": "<@UAAAAAAAA> uploaded a file: <https://fake.slack."
                         "com/files/UAAAAAAAA/id/img.jpg|img.jpg> and "
                         "commented: bla",
                 "ts": "1524724685.000201",
                 "type": "message",
                 "upload": True,
                 "user": "UAAAAAAAA",
                 "username": "bob"}


class FakeArgs(object):
    token = 'token_string'
    user = 'fake_user'
    password = 'fake_password'
    team = 'fake_team'
    database = None
    channels = None
    url_file_to_attachment = False

    def __contains__(self, key):
        return hasattr(self, key)


class TestApiCalls(unittest.TestCase):

    def test_channels_list(self):
        cl = client.Client(FakeArgs())
        cl.slack.api_call = mock.MagicMock(return_value=CHANNELS)
        channels = cl._channels_list()
        self.assertListEqual(CHANNELS['channels'], channels)

    def test_users_list(self):
        cl = client.Client(FakeArgs())
        cl.slack.api_call = mock.MagicMock(return_value=USERS)
        users = cl._users_list()
        self.assertListEqual(USERS['members'], users)

    def test_channels_history(self):
        cl = client.Client(FakeArgs())

        cl.slack.api_call = mock.MagicMock(return_value=USERS)
        cl.downloader._download = mock.MagicMock(return_value=None)
        cl.update_users()

        cl.slack.api_call = mock.MagicMock(return_value=CHANNELS)
        cl.update_channels()

        cl.slack.api_call = mock.MagicMock()
        cl.slack.api_call.side_effect = [MSGS, MSG2, MSG3]

        channel = cl.q(o.Channel).filter(o.Channel.slackid ==
                                         "C00000001").one()

        msg, ts = cl._channels_history(channel, 0)
        self.assertEqual(len(msg), 6)
        self.assertEqual(ts, '1479501074.000032')

        msg, ts = cl._channels_history(channel, ts)
        self.assertEqual(len(msg), 1)
        self.assertEqual(ts, '1479505026.000002')

        msg, ts = cl._channels_history(channel, ts)
        self.assertEqual(len(msg), 0)
        self.assertIsNone(ts)


class TestClient(unittest.TestCase):

    def test_update_users(self):
        cl = client.Client(FakeArgs())
        cl.slack.api_call = mock.MagicMock(return_value=USERS)
        cl.downloader._download = mock.MagicMock(return_value=None)
        cl.update_users()
        users = cl.session.query(o.User).all()
        self.assertEqual(len(users), 4)
        self.assertEqual(users[0].id, 1)

        cl.update_users()
        users = cl.session.query(o.User).all()
        self.assertEqual(len(users), 4)
        self.assertEqual(users[0].id, 1)
        self.assertEqual(users[0].slackid, 'UAAAAAAAA')


class TestMessage(unittest.TestCase):

    def setUp(self):
        args = FakeArgs()
        args.channels = ['general']

        self.cl = client.Client(args)
        self.cl.downloader.authorize = mock.MagicMock()
        self.cl.slack.api_call = mock.MagicMock(return_value=USERS)
        self.cl.downloader._download = mock.MagicMock(return_value=None)
        self.cl.update_users()

        self.cl.slack.api_call = mock.MagicMock(return_value=CHANNELS)
        self.cl.update_channels()

        self.cl.slack.api_call = mock.MagicMock()

    @mock.patch('slack_backup.download.Download.download')
    def test_update_history(self, download):

        download.return_value = 'foo'

        self.cl.downloader._download = mock.MagicMock(return_value=None)
        self.cl.slack.api_call.side_effect = [MSGS, MSG3]
        self.cl.update_history()
        self.assertEqual(len(self.cl.q(o.Message).all()), 5)

        self.cl.slack.api_call.side_effect = [MSG2, MSG3]
        self.cl.update_history()

        self.assertEqual(len(self.cl.q(o.Message).all()), 6)


class TestCreateMessage(unittest.TestCase):

    @mock.patch('slack_backup.client.Client._file_data')
    @mock.patch('slack_backup.client.Client._get_user')
    def test_empty_message(self, gu, fd):
        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value='aa')
        cl.session = mock.MagicMock()
        channel = o.Channel({'name': 'test', 'id': 'C00000001'})

        cl._create_message({'type': 'message', 'text': ''}, channel)
        cl.session.add.assert_not_called()

    @mock.patch('slack_backup.client.Client._file_data')
    @mock.patch('slack_backup.client.Client._get_user')
    def test_message_with_reaction(self, gu, fd):
        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value='aa')
        cl.session = mock.MagicMock()
        channel = o.Channel({'name': 'test', 'id': 'C00000001'})

        cl._create_message(MSGS['messages'][1], channel)

        msg = cl.session.add.call_args[0][0]
        self.assertEqual(len(msg.attachments), 1)
        self.assertEqual(len(msg.reactions), 1)
        self.assertEqual(msg.reactions[0].name, '+1')
        self.assertFalse(msg.is_starred)

    @mock.patch('slack_backup.client.Client._get_user')
    def test_starred_item(self, gu):
        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value='aa')
        cl.session = mock.MagicMock()
        channel = o.Channel({'name': 'test', 'id': 'C00000001'})

        data = {"type": "message",
                "user": "UAAAAAAAA",
                "text": "test",
                "ts": "1479501074.000032",
                "is_starred": True}
        cl._create_message(data, channel)

        msg = cl.session.add.call_args[0][0]
        self.assertEqual(len(msg.attachments), 0)
        self.assertEqual(msg.text, 'test')
        self.assertEqual(msg.type, '')
        self.assertTrue(msg.is_starred)

    @mock.patch('slack_backup.client.Client._file_data')
    @mock.patch('slack_backup.client.Client._get_user')
    def test_external_file_upload(self, gu, fd):
        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value='aa')
        cl.session = mock.MagicMock()
        channel = o.Channel({'name': 'test', 'id': 'C00000001'})

        cl._create_message(SHARED, channel)

        msg = cl.session.add.call_args[0][0]
        self.assertEqual(len(msg.attachments), 0)
        self.assertTrue('shared a file' in msg.text)
        self.assertFalse(msg.is_starred)
        self.assertEqual(msg.type, 'file_share')
        fd.assert_called_once_with(msg, SHARED['file'])

    @mock.patch('slack_backup.client.Client._get_user')
    def test_external_file_upload_as_attachment(self, gu):
        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value='aa')
        cl.session = mock.MagicMock()
        cl._url_file_to_attachment = True
        channel = o.Channel({'name': 'test', 'id': 'C00000001'})

        cl._create_message(SHARED, channel)

        msg = cl.session.add.call_args[0][0]
        self.assertEqual(len(msg.attachments), 1)
        self.assertTrue('shared a file' in msg.text)
        self.assertFalse(msg.is_starred)

    @mock.patch('slack_backup.client.Client._file_data')
    @mock.patch('slack_backup.client.Client._get_user')
    def test_pinned_message_with_attachments(self, gu, fd):
        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value='aa')
        cl.session = mock.MagicMock()
        cl._url_file_to_attachment = True
        channel = o.Channel({'name': 'test', 'id': 'C00000001'})

        cl._create_message(PINNED, channel)

        msg = cl.session.add.call_args[0][0]
        self.assertEqual(len(msg.attachments), 1)
        self.assertEqual(msg.text, '<@UAAAAAAAA> pinned a message to this '
                         'channel.')
        self.assertEqual(msg.type, 'pinned_item')
        self.assertEqual(msg.attachments[0].text, 'the text')
        self.assertEqual(msg.attachments[0].title, 'Fake service title')


class TestFileShare(unittest.TestCase):

    @mock.patch('slack_backup.download.Download.download')
    @mock.patch('slack_backup.utils.makedirs')
    def test_file_data(self, md, dl):
        dl.side_effect = ['some_path']

        url = INTERNAL_DATA['file']['url_private_download']

        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value=url)
        cl.session = mock.MagicMock()

        msg = o.Message()
        cl._file_data(msg, INTERNAL_DATA['file'])

        self.assertIsNotNone(msg.file)
        self.assertEqual(msg.file.filepath, 'some_path')

    @mock.patch('slack_backup.download.Download.download')
    @mock.patch('slack_backup.utils.makedirs')
    def test_starred_file_data(self, md, dl):
        dl.side_effect = ['some_path']

        data = copy.deepcopy(INTERNAL_DATA)
        data['file']['is_starred'] = True
        url = data['file']['url_private_download']

        cl = client.Client(FakeArgs())
        cl.downloader._download = mock.MagicMock(return_value=url)
        cl.session = mock.MagicMock()

        msg = o.Message()
        cl._file_data(msg, data['file'])

        self.assertTrue(msg.is_starred)

    @mock.patch('uuid.uuid4')
    @mock.patch('slack_backup.download.Download.download')
    @mock.patch('slack_backup.utils.makedirs')
    def test_external_file_data(self, md, dl, uuid):
        uuid.side_effect = ['aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee']
        dl.side_effect = ['some_path']

        # url = EXTERNAL_DATA['file']['url_private']

        cl = client.Client(FakeArgs())
        cl.session = mock.MagicMock()

        # pretend, that we are authorized
        cl.downloader._authorized = True

        msg = o.Message()
        expexted_line = ('https://docs.google.com/spreadsheets/d/xxx/edit?'
                         'usp=drivesdk --> '
                         'assets/files/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n')

        cl._file_data(msg, EXTERNAL_DATA['file'])
        file_ = cl.session.add.call_args[0][0]
        self.assertEqual(cl._dldata, [expexted_line])
        self.assertEqual(file_.filepath,
                         'assets/files/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee')

        dl.assert_not_called()


if __name__ == "__main__":
    unittest.main()
