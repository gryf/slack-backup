Slack backup
============

.. image:: https://travis-ci.org/gryf/slack-backup.svg?branch=master
    :target: https://travis-ci.org/gryf/slack-backup

This simple project which aim is to collect conversations from Slack using its
API and optionally user account information, and provides convenient way to
represent as a log.

Requirements
------------

This project is written in Python 2.7, and 3.4+, although version 2.7, which
should work, wasn't tested as extensively as it should be.

Other than that, required packages are as follows:

- slackclient 1.0.2
- SQLAlchemy 1.0.10

Installation
------------

You can install it using ``pip install slack-backup`` command. Recommended way
is to create virtualenv, like so:

.. code:: shell-session

   user@localhost $ virtualenv -p python3 myenv
   Running virtualenv with interpreter /usr/bin/python3
   Using base prefix '/usr'
   New python executable in foobar/bin/python3
   Also creating executable in foobar/bin/python
   Installing setuptools, pip, wheel...done.
   user@localhost $ . myenv/bin/activate
   (myenv)user@localhost $ pip install slack-backup

You can also get this repository and install from it, like:

.. code:: shell-session

   user@localhost ~ $ virtualenv -p python3 myenv
   Running virtualenv with interpreter /usr/bin/python3
   Using base prefix '/usr'
   New python executable in foobar/bin/python3
   Also creating executable in foobar/bin/python
   Installing setuptools, pip, wheel...done.
   user@localhost $ . myenv/bin/activate
   (myenv)user@localhost ~ $ cd myenv
   (myenv)user@localhost ~/myenv $ git clone https://github.com/gryf/slack-backup
   (myenv)user@localhost ~/myenv $ cd slack-backup
   (myenv)user@localhost ~/myenv/slack-backup $ pip install .

Usage
-----

There is a commandline tool called `slack-backup`, which typical use would get
to gather the data and generate logs. Using example from above, here is a
typical session:

.. code:: shell-session

   (myenv)user@localhost ~/myenv/slack-backup $ mkdir ~/mylogs && cd ~/mylogs
   (myenv)user@localhost ~/mylogs $ slack-backup fetch \
   --token xxxx-1111111111-222222222222-333333333333-r4nd0ms7uff \
   --user some@email.address.org --password secret --team myteam \
   -qqq -d mydatabase.sqlite

where:

* ``--token`` is generated on `Slack side token`_ for interaction with the API.
  It's required.
* ``--user`` is your slack account username…
* ``--password`` …and password. Those two are needed if you care about files
  posted on the channels, which are hosted on Slack servers. They can be
  skipped, if you don't care about such files. Avatars still be downloaded
  though. External resources will not be downloaded - they have URL anyway.
* ``--team`` team name. It is the part of the URL for your slack team; in other
  words in URL like `http://foobar.slack.com` *foobar* is the team name.
* ``-q`` (or ``--quiet``) will suppress any messages from program. In contrary
  there can be used ``--verbose`` to increase verbosity. Using this option
  several times (up to three, above the number will have no effect) will amplify
  effectiveness of either be quite or be verbose behaviour.
* ``-d`` or ``--database`` is the file path for database (which for now at least
  is an sqlite database file). It can be omitted - in-memory db would be
  created, but you'll (obviously) lost all the records. Besides the db file,
  assets directory might be created for downloadable items.

During DB creation, all available messages are stored in the database. On the
next run, ``fetch`` would only take those records, which are older from
currently oldest in DB. So that it will only fetch a subset of the overall of
the messages. As for the channels and users - complete information will be
downloaded every time ``fetch`` command would be used.

Next, to generate a log files:

.. code:: shell-session

   (myenv)user@localhost ~/mylogs $ slack-backup generate \
   -v -d mydatabase.sqlite --format text -o logs

where:

* ``--format`` is the desired format of the logs. For now only ``text`` format
  of the logs is supported (IRC style format). Format ``none`` will produce
  nothing.
* ``-o`` or ``--output`` is the destination directory, where logs and possible
  assets will land.

The rest of the options (``-d`` and ``-v``) have same meaning as in ``fetch``
command.


License
-------

This work is licensed on 3-clause BSD license. See LICENSE file for details.

.. _Slack side token: https://api.slack.com/docs/oauth-test-tokens
