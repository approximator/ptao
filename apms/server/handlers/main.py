import os
import logging

from tornado.web import RequestHandler

from apms.lib.config import config

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class MainHandler(RequestHandler):
    """
    Redirects to ui
    """

    def get(self, file_name='index.html'):  # pylint: disable=arguments-differ
        log.debug('MainHandler {}'.format(file_name))
        self.write(open(os.path.join(config.static_dir, 'index.html')).read())
