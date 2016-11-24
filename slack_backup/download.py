"""
Module for download files, store them in local filesystem and convert the URLs
to local ones, so that sophisticated writers can make a use of it
"""
import logging
import os
import errno

import requests


class NotAuthorizedError(requests.HTTPError):
    pass


class Download(object):
    """Download class for taking care of Slack internally uploaded files"""

    def __init__(self, args):
        self.session = requests.session()
        self.team = args.team
        self.user = args.user
        self.password = args.password
        self.assets_dir = args.assets
        self._files = os.path.join(self.assets_dir, 'files')
        self._images = os.path.join(self.assets_dir, 'images')
        self._do_download = False
        self._hier_created = False
        self.cookies = {}

    def download(self, url, filetype):
        """
        Download asset, return local path to it
        """
        if not self._do_download:
            return

        if not self._hier_created:
            self._create_assets_dir()

        fname = self.prepare_filepath(url, filetype)

        self._download(url, fname)
        return fname

    def _create_assets_dir(self):
        for name in ('images', 'files'):
            try:
                os.makedirs(os.path.join(self.assets_dir, name))
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise

        self._hier_created = True

    def prepare_filepath(self, url, filetype):
        """Prepare directory where to download file into"""

        typemap = {'avatar': self._images,
                   'file': self._files}

        splitted = url.split('/')

        if len(splitted) == 7 and 'slack.com' in splitted[2]:
            part = url.split('/')[-3]
            fname = url.split('/')[-1]
        else:
            logging.info("URL doesn't seem to be slack internal: %s", url)
            part = ''
            fname = splitted[-1]

        path = typemap[filetype]

        if part:
            try:
                path = os.path.join(path, part)
                os.makedirs(path)
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise

        path = os.path.join(path, fname)
        count = 1

        while os.path.exists(path):
            base, ext = os.path.splitext(path)
            path = base + "%0.3d" % count + ext

        return path

    def _download(self, url, local):
        """Download file"""

        res = self.session.get(url, stream=True)
        with open(local, 'wb') as fobj:
            for chunk in res.iter_content(chunk_size=5120):
                if chunk:
                    fobj.write(chunk)

    def authorize(self):
        """
        Authenticate and gather session for Slack
        """
        res = self.session.get('https://%s.slack.com/' % self.team)
        if not all((self.team, self.password, self.user)):
            logging.warning('There is neither username, password or team name'
                            ' provided. Downloading will not be performed.')
            return

        crumb = ''
        for line in res.text.split('\n'):
            if 'crumb' in line:
                crumb = line.split('value=')[1].split('"')[1]
                break
        else:
            logging.error('Cannot access Slack login page')
            return

        res = self.session.post("https://%s.slack.com/" % self.team,
                                {'crumb': crumb,
                                 'email': self.user,
                                 'password': self.password,
                                 'signin': 1})
        self.cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        if not ('a' in self.cookies and 'b' in self.cookies and
                ('a-' + self.cookies['a']) in self.cookies):
            logging.error('Failed to login into Slack app')
        else:
            self._do_download = True
