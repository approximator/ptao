import logging

from tornado.web import RequestHandler

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class SwaggerSpecHandler(RequestHandler):
    """
    Returns swagger docs yml
    """

    def initialize(self, spec):
        """
        Save spec, so it can be returned on request
        """
        self._spec = spec  # pylint: disable=attribute-defined-outside-init

    def get(self):
        """
        Handler for /swagger/main.yml
        """
        self.set_header('Content-Type', 'application/x-yaml')
        self.write(self._spec.to_yaml())
