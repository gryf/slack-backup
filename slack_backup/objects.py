#!/usr/bin/env python3
"""
Convinient object mapping from slack API reponses
"""

class Base(object):
    def __init__(self, data_dict=None):
        data_dict = data_dict or {}
        self.creator = data_dict.get('creator', '')
        self.last_set = data_dict.get('last_set', 0)
        self.value = data_dict.get('value')

    def __repr__(self):
        return u"<%s %s>" % (str(hex(id(self))), self.__unicode__())

    def __unicode__(self):
        return u", %s" % self.value


class Purpose(Base):
    pass


class Topic(Base):
    pass


class BaseObject(object):
    def __init__(self):
        self._id = None
        self.name = None

    def __repr__(self):
        return u"<%s %s>" % (str(hex(id(self))), self.__unicode__())

    def __unicode__(self):
        return u"%s, %s %s" % (self.__class__.__name__, self._id, self.name)


class Channel(BaseObject):
    def __init__(self, data_dict=None):
        super().__init__()

        data_dict = data_dict or {}

        self._id = data_dict['id']
        self.name = data_dict['name']
        self.created = data_dict.get('created', '')
        self.creator = data_dict.get('created', '')
        self.is_archived = data_dict.get('created', '')
        self.is_channel = True,
        self.is_general = data_dict['is_general']
        self.members = data_dict.get('members', [])

        self.purpose = Purpose(data_dict.get('purpose'))
        self.topic = Topic(data_dict.get('topic'))


class UserProfile(object):
    def __init__(self, data_dict=None):
        super().__init__()

        data_dict = data_dict or {}

        self.first_name = data_dict.get("first_name", "")
        self.last_name = data_dict.get("last_name", "")
        self.real_name = data_dict.get("real_name", "")
        self.email = data_dict.get("email", "")
        self.skype = data_dict.get("skype", "")
        self.phone = data_dict.get("phone", "")
        self.image_24 = data_dict.get("image_24", "")
        self.image_32 = data_dict.get("image_32", "")
        self.image_48 = data_dict.get("image_48", "")
        self.image_72 = data_dict.get("image_72", "")
        self.image_192 = data_dict.get("image_192", "")
        self.image_512 = data_dict.get("image_512", "")


class User(BaseObject):
    def __init__(self, data_dict=None):
        data_dict = data_dict or {}

        self._id = data_dict.get("id", "")
        self.name = data_dict.get("name", "")
        self.deleted = data_dict.get("deleted", False)
        self.color = data_dict.get("color", "")
        self.is_admin = data_dict.get("is_admin", False)
        self.is_owner = data_dict.get("is_owner", False)
        self.is_primary_owner = data_dict.get("is_primary_owner", False)
        self.is_restricted = data_dict.get("is_restricted", False)
        self.is_ultra_restricted = data_dict.get("is_ultra_restricted", False)
        self.has_2fa = data_dict.get("has_2fa", False)
        self.two_factor_type = data_dict.get("two_factor_type", "")
        self.has_files = data_dict.get("has_files", False)

        self.profile = UserProfile(data_dict.get("profile"))
