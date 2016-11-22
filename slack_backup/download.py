"""
Module for download files, store them in local filesystem and convert the URLs
to local ones, so that sophisticated writers can make a use of it
"""
import logging

import requests


class NotAuthorizedError(requests.HTTPError):
    pass


class Download(object):
    """Download class for taking care of Slack internally uploaded files"""

    def __init__(self, user, password, team):
        self.session = requests.session()
        self.team = team
        self.user = user
        self.password = password

    def get_local_url(self, url):
        """
        Download file from provided url and save it locally. Return local URI.
        """
        # TODO: implementation
        # res = session.post(url)
        # new_path = self.prepare_uri(url)
        # with open(new_path, "wb") as fobj:
        #     fobj.write(p.content)
        # return url

        return url

    def authorize(self):
        """
        Authenticate and gather session for Slack
        """
        res = self.session.get('https://%s.slack.com/' % self.team)

        crumb = ''
        for line in res.text.split('\n'):
            if 'crumb' in line:
                crumb = line.split('value=')[1].split('"')[1]
                break
        else:
            logging.error('Cannot access Slack login page')
            raise NotAuthorizedError('Cannot access Slack login page')

        res = self.session.post("https://%s.slack.com/" % self.team,
                                {'crumb': crumb,
                                 'email': self.user,
                                 'password': self.password,
                                 'signin': 1})
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        if not ('a' in cookies and 'b' in cookies and
                ('a-' + cookies['a']) in cookies):
            raise NotAuthorizedError('Failed to login into Slack app')
