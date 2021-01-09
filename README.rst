Slack backup
============

.. image:: https://travis-ci.org/gryf/slack-backup.svg?branch=master
    :target: https://travis-ci.org/gryf/slack-backup

.. image:: https://img.shields.io/pypi/v/slack-backup.svg
    :target: https://pypi.python.org/pypi/slack-backup

**This project has been archived.**

The project aim is to collect conversations from Slack using its API and
optionally user account information, and provides convenient way to represent
as a log.

Requirements
------------

This project is written in Python 3, 3.4 to be precise (currently it works with
version 3.6), although it may work on earlier version of Python3. Sorry no
support for Python2.

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
   -qq -d mydatabase.sqlite

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

You can also specify directory, where pure response JSONs from Slack API will
be stored by using ``-r/--raw-dir`` or by providing it in config file in
``fetch`` section as ``raw_dir`` (note the underscore in config file contrary
to the swith, which have hyphen between ``raw`` and ``dir``). This might be useful for
debugging purposes.

There is one more switch to take into consideration -
``-f/--url-file-to-attachment`` which influence the way how external file
share would be treated. First of all, what is *external* file share from slack
point of view, one could ask. Slack have some sort of integration with Google
services, like Google Drive, which provide slack users to create or "upload"
files from Google Drive. "Upload", since no uploading actually takes place,
and only URL is provided for such "uploads". By default `slack-backup` will
create a file which is prefixed ``manual_download_`` which will contain URL and
destination path to the file, where user should manual download file to.
Example file contents:

.. code::

   http://foo.bar.com/some/file --> assets/files/83340cbe-fee2-4d2e-bdb1-cace9c82e6d4
   http://foo.bar.com/some/other/file --> assets/files/8a4c873c-1864-4f1b-b515-bbef119f33a3
   http://docs/google.com/some/gdoc/file --> assets/files/ec8752bc-0bf8-4743-a8bd-9756107ab386

By setting ``--url-file-to-attachment`` flag (or making an option
``url_file_to_attachment`` set to ``true`` in config file) such "uploads" would
be internally converted into Slack "attachment", which internally is an object
to store external links, so there is no need for user interaction.

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

See help for the ``slack-backup`` command for complete list of options.

Configuration
-------------

For convenience, you can place all of needed options into configuration file
(aka .ini), which all options (with their defaults) will look like:

.. code:: ini

   [common]
   channels =
   database =
   quiet = 0
   verbose = 0

   [generate]
   output =
   format = text
   theme = plain

   [fetch]
   url_file_to_attachment = false
   user =
   password =
   team =
   token =
   raw_dir =

Note, that you don't have to put every option. To illustrate ``fetch`` example
from above, here is a corresponding config file:

.. code:: ini

   [common]
   database = mydatabase.sqlite
   quiet = 2

   [fetch]
   user = some@email.address.org
   password = secret
   team = myteam
   token = xxxx-1111111111-222222222222-333333333333-r4nd0ms7uff

Note, that only ``[common]`` and ``[fetch]`` sections are provided, so it is
enough to invoke ``slack-backup`` command as:

.. code:: shell-session

   (myenv)user@localhost ~/mylogs $ slack-backup fetch

There are couple of places, where configuration file would be searched for, in
particular order:

* file provided via argument ``-i`` or ``--config``
* ``slack-backup.ini`` in current directory
* ``$XDG_CONFIG_HOME/slack-backup.ini``, where ``$XDG_CONFIG_HOME`` usually
  defaults to ``$HOME/.config``

Details
-------

During first run, database with provided name is generated. For ease of use
sqlite database is used, although it is easy to switch the engine, since there
is an ORM (SQLAlchemy) used.

Slack users, channels and messages are mapped to SQLAlchemy models, as well as
other information, like:

- user profiles
- channel topic
- channel purpose
- message reactions
- message attachments
- and files

Channels and users are always synchronized in every run, so every modification
to the user or channels are overwriting old data. During first run, all messages
are retrieved for all/selected channels. Every other run will only fetch those
messages, which are older then newest message in the database - so that we don't
loose any old messages, which might be automatically removed from Slack servers.
The drawback of this behaviour is that all past messages which was altered in
the meantime will not be updated.

License
-------

This work is licensed on 3-clause BSD license. See LICENSE file for details.

.. _Slack side token: https://api.slack.com/docs/oauth-test-tokens
