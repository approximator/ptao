import json
import logging

from tornado.web import RequestHandler

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class SwaggerSpecHandler(RequestHandler):
    """
    Returns swagger docs json
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
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(self._spec.to_dict()))
