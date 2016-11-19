"""
Common db functions
"""
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Prepare SQLAlchemy objects
Meta = MetaData()
Base = declarative_base(metadata=Meta)
Session = sessionmaker()
DbFilename = None


def connect(filename=None):
    """
    create engine and bind to Meta object.
    Arguments:
        @filename - string with absolute or relative path to sqlite database
                    file. If None, db in-memory will be created
    """
    global DbFilename

    if not filename:
        filename = ':memory:'

    DbFilename = filename

    connect_string = "sqlite:///%s" % filename
    engine = create_engine(connect_string)
    Meta.bind = engine
    Meta.create_all(checkfirst=True)
    return engine
