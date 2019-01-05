"""
Convinient object mapping from slack API reponses
"""
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship

from slack_backup.db import Base
from slack_backup import utils


class Purpose(Base):
    __tablename__ = 'purposes'

    id = Column(Integer, primary_key=True)
    last_set = Column(DateTime)
    value = Column(Text)

    creator_id = Column(Integer, ForeignKey('users.id'), index=True)
    creator = relationship("User", back_populates="purposes")

    channel_id = Column(Integer, ForeignKey('channels.id'), index=True)
    channel = relationship("Channel", back_populates="purpose")

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict):
        data_dict = data_dict or {}
        self.last_set = utils.fromtimestamp(data_dict.get('last_set'))
        self.value = data_dict.get('value')

    def __repr__(self):
        return u'<%s %s>' % (str(hex(id(self))), self.__unicode__())

    def __unicode__(self):
        return u', %s %s' % (self.id, self.value)


class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    last_set = Column(DateTime)
    value = Column(Text)

    channel_id = Column(Integer, ForeignKey('channels.id'), index=True)
    channel = relationship("Channel", back_populates="topic")

    creator_id = Column(Integer, ForeignKey('users.id'), index=True)
    creator = relationship("User", back_populates="topics")

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict):
        data_dict = data_dict or {}
        self.last_set = utils.fromtimestamp(data_dict.get('last_set'))
        self.value = data_dict.get('value')

    def __repr__(self):
        return u'<%s %s>' % (str(hex(id(self))), self.__unicode__())

    def __unicode__(self):
        return u', %s %s' % (self.id, self.value)


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    slackid = Column(Text)
    name = Column(Text)
    created = Column(DateTime)
    is_archived = Column(Boolean, default=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True,
                        index=True)
    creator = relationship("User", back_populates="channels")

    purpose = relationship("Purpose", uselist=False, back_populates="channel")
    topic = relationship("Topic", uselist=False, back_populates="channel")
    messages = relationship("Message", back_populates="channel")

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict):
        data_dict = data_dict or {}

        self.slackid = data_dict.get('id', '')
        self.name = data_dict.get('name', '')
        self.created = utils.fromtimestamp(data_dict.get('created'))
        self.is_archived = data_dict.get('is_archived', False)

    def __repr__(self):
        return u'<%s %s>' % (str(hex(id(self))), self.__unicode__())

    def __unicode__(self):
        return u'%s, %s %s' % (self.__class__.__name__, self.id, self.name)


class UserProfile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)

    avatar_hash = Column(Text)
    email = Column(Text)
    first_name = Column(Text)
    image_192 = Column(Text)
    image_24 = Column(Text)
    image_32 = Column(Text)
    image_48 = Column(Text)
    image_72 = Column(Text)
    image_original = Column(Text)
    last_name = Column(Text)
    real_name = Column(Text)
    real_name_normalized = Column(Text)
    image_path = Column(Text)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="profile")

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict):
        data_dict = data_dict or {}

        self.avatar_hash = data_dict.get('avatar_hash', '')
        self.email = data_dict.get("email", '')
        self.first_name = data_dict.get('first_name', '')
        self.image_192 = data_dict.get('image_192', '')
        self.image_24 = data_dict.get('image_24', '')
        self.image_32 = data_dict.get('image_32', '')
        self.image_48 = data_dict.get('image_48', '')
        self.image_72 = data_dict.get('image_72', '')
        self.image_original = data_dict.get('image_original', '')
        self.last_name = data_dict.get('last_name', '')
        self.real_name = data_dict.get('real_name', '')
        self.real_name_normalized = data_dict.get('real_name_normalized', '')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    deleted = Column(Boolean, default=False)
    name = Column(Text)
    real_name = Column(Text)
    slackid = Column(Text)

    channels = relationship("Channel", back_populates="creator")
    messages = relationship("Message", back_populates="user")
    profile = relationship("UserProfile", uselist=False, back_populates="user")
    purposes = relationship("Purpose", back_populates="creator")
    topics = relationship("Topic", back_populates="creator")
    reaction_id = Column(Integer, ForeignKey("reactions.id"))
    reaction = relationship("Reaction", back_populates="users")

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict=None):
        data_dict = data_dict or {}

        self.deleted = data_dict.get('deleted', False)
        self.name = data_dict.get("name", '')
        self.real_name = data_dict.get('real_name', '')
        self.slackid = data_dict.get('id', '')

        if not self.profile:
            self.profile = UserProfile(data_dict.get('profile'))
        else:
            self.profile.update(data_dict.get('profile'))

    def __repr__(self):
        return u'<%s %s>' % (str(hex(id(self))), self.__unicode__())

    def __unicode__(self):
        return u'%s, %s %s' % (self.__class__.__name__, self.id, self.name)


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    users = relationship("User", back_populates="reaction")

    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    message = relationship("Message", back_populates="reactions")

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict):
        data_dict = data_dict or {}

        self.name = data_dict.get('name', '')


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    # NOTE(gryf): timestamps from messages are coming as text. It might be
    # tempting to store them as Decimal or Integer, but it doesn't really
    # matters since in case of Decimal sqlite doesn't support it, and Integer
    # require additional conversion. It might be critical for messages to have
    # exact timestamp including microseconds, since it will be extracted for
    # API query. Such query have an option for specify timestam which is the
    # oldest, that's why it could be easy to lost some messages if the
    # difference would be on microseconds level.
    ts = Column(Text, index=True)
    text = Column(Text)
    type = Column(Text)
    is_starred = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True,
                     index=True)
    user = relationship("User", back_populates="messages")

    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True,
                        index=True)
    channel = relationship("Channel", back_populates="messages")

    reactions = relationship("Reaction", back_populates="message")
    files = relationship("File", back_populates="message")
    attachments = relationship("Attachment", back_populates="message")

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def datetime(self):
        return utils.fromtimestamp(float(self.ts))

    def update(self, data_dict):
        data_dict = data_dict or {}

        self.ts = data_dict.get('ts', 0)
        self.text = data_dict.get('text', '')
        self.type = data_dict.get('subtype', '')


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    url = Column(Text)
    name = Column(Text)
    title = Column(Text)
    filepath = Column(Text)

    message_id = Column(Integer, ForeignKey('messages.id'))
    message = relationship('Message', back_populates='files')

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict):
        data_dict = data_dict or {}

        self.name = data_dict.get('name', '')
        self.title = data_dict.get('title', '')


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    fallback = Column(Text)
    text = Column(Text)

    message_id = Column(Integer, ForeignKey('messages.id'))
    message = relationship('Message', back_populates='attachments')

    def __init__(self, data_dict=None):
        self.update(data_dict)

    def update(self, data_dict):
        data_dict = data_dict or {}

        self.title = data_dict.get('title', '')
        self.text = data_dict.get('text', '')
        self.fallback = data_dict.get('fallback', '')
