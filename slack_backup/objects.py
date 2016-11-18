"""
Convinient object mapping from slack API reponses
"""

class Purpose(object):
    def __init__(self, data_dict=None):
        data_dict = data_dict or {}
        self.creator = data_dict.get('creator', '')
        self.last_set = data_dict.get('last_set', 0)
        self.value = data_dict.get('value')


class Topic(object):
    def __init__(self, data_dict=None):
        data_dict = data_dict or {}
        self.creator = data_dict.get('creator', '')
        self.last_set = data_dict.get('last_set', 0)
        self.value = data_dict.get('value')


class Channel(object):
    def __init__(self, id_, name, topic):
        self._id = id_
        self.name = name
        self.topic = topic
        self.created = None
        self.creator = None
        self.is_archived = False,
        self.is_channel = True,
        self.is_general = False,
        self.is_member = True,
        self.members = []
        self.purpose': {u'creator': u'', u'last_set': 0, u'value': u''},
        topic':

