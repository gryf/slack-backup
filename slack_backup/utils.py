"""
Some utils functions. Jsut to not copypaste the code around
"""
from datetime import datetime
import errno
import os
import logging
import tempfile
import hashlib


def makedirs(path):
    """Create if not exists - version of os.makedirs."""
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno != errno.EEXIST:
            logging.error("Cannot create `%s'.", path)
            raise
        else:
            if os.path.exists(path) and not os.path.isdir(path):
                logging.error("Cannot create `%s'. There is some file on the "
                              "way; cannot proceed.", path)
                raise


def get_temp_name(suffix='', prefix='tmp', dir=None, unlink=False):
    """Return temporary file name"""
    fdesc, fname = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    os.close(fdesc)
    if unlink:
        os.unlink(fname)
    return fname


def same_files(file1, file2):
    """
    Compare files by calculating hash for each of them. Return True if hash is
    identical, False otherwise
    """
    with open(file1, 'rb') as fobj:
        hash1 = hashlib.sha256(fobj.read())

    with open(file2, 'rb') as fobj:
        hash2 = hashlib.sha256(fobj.read())

    return hash1.hexdigest() == hash2.hexdigest()


def fromtimestamp(timestamp):
    """
    Return datetime object from provided timestamp. If timestamp argument is
    falsy, datetime object placed in January 1970 will be retuned.
    """
    if not timestamp:
        return datetime.utcfromtimestamp(0)
    return datetime.fromtimestamp(timestamp)
