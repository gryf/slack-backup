#!/usr/bin/env python3
"""
Setup for the slack-backup project
"""
from distutils.core import setup


setup(name="slack-backup",
      packages=["slack_backup"],
      version="0.0",
      description="Make copy of slack converstaions",
      author="Roman Dobosz",
      author_email="gryf73@gmail.com",
      url="https://github.com/gryf/slack-backup",
      download_url="https://github.com/gryf/slack-backup",
      keywords=["chat", "backup", "history", "slack"],
      install_requires=["sqlalchemy", "slackclient"],
      scripts=["scripts/slack-backup"],
      classifiers=["Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.4",
                   "Development Status :: 2 - Pre-Alpha",
                   "Environment :: Console",
                   "Intended Audience :: End Users/Desktop",
                   "License :: OSI Approved :: BSD License",
                   "Operating System :: OS Independent",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Database :: Front-Ends",
                   "Topic :: Communications :: Chat",
                   "Topic :: Text Processing :: Markup",
                   "Topic :: Text Processing :: Markup :: HTML"],
      long_description=open("README.rst").read(),
      options={'test': {'verbose': False,
                        'coverage': False}})
