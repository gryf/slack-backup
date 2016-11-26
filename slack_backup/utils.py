"""
Some utils functions. Jsut to not copypaste the code around
"""
import errno
import os
import logging


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
