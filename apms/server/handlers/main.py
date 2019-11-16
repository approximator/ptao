import os
import logging

from tornado.web import RequestHandler

from apms.lib.config import config

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class MainHandler(RequestHandler):
    """
    Returns the specified static file
    """

    def get(self, file_name="index.html"):  # pylint: disable=arguments-differ
        """Get specified file
        ---
        summary: Get file from static directory
        tags:
          - "Files"
        parameters:
          - name: file_name
            required: false
            in: path
            schema:
              type: string

        responses:
          200:
            description: File content
          404:
            description: Not found
        """
        log.debug("MainHandler {}".format(file_name))
        self.write(open(os.path.join(config.static_dir, file_name)).read())
