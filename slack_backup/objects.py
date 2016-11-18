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


class Channel(object):
    def __init__(self, data_dict=None):
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

    def __repr__(self):
        return u"<%s %s>" % (str(hex(id(self))), self.__unicode__())

    def __unicode__(self):
        return u"channel, %s %s" % (self._id, self.name)

