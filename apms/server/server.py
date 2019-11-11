# -*- coding: utf-8 -*-
"""
Copyright © 2018 Approximator. All rights reserverd.
Author: Approximator (alex@nls.la)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging

import tornado
from tornado.web import Application, StaticFileHandler
from tornado_sqlalchemy import make_session_factory

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin

from ..lib.config import config
from .handlers.main import MainHandler
from .handlers.photos import PhotosHandler
from .handlers.swagger import SwaggerSpecHandler
from .handlers.users import UsersHandler, UsersUpdateHandler
from .handlers.photos import PeopleTagHandler
from .updater import Updater

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
logging.getLogger('tornado').setLevel(logging.WARNING)


class ApmsServer:

    def __init__(self, config_file=None):
        config.load_config(config_file if config_file is not None else config.default_config_file())

        self._spec = APISpec(title='APMS API',
                             version='1.0.1',
                             openapi_version='3.0.0',
                             info=dict(description='APMS API'),
                             plugins=[
                                 TornadoPlugin(),
                                 MarshmallowPlugin(),
                             ])

        api_urls = [
            (r"/api/photos", PhotosHandler),  #
            (r"/api/photos/tagPeople", PeopleTagHandler),  #
            (r"/api/users/(.+)/update", UsersUpdateHandler),  #
            (r"/api/users", UsersHandler),  #
        ]

        other_urls = [
            (r"/swagger/main.json", SwaggerSpecHandler, dict(spec=self._spec)),  #
            (r'/files/photos/(.*)', StaticFileHandler, {
                'path': config.photos_dir
            }),
            (r'/', MainHandler),
            (r'/photos', MainHandler),
            (r'/people', MainHandler),
            (r'/api-docs', MainHandler),
            (r'/(.*)', StaticFileHandler, {
                'path': config.static_dir
            })
        ]

        for url in api_urls:
            self._spec.path(urlspec=url)

        self._session_factory = make_session_factory(config.db_connection_string)
        self._updater = Updater(config, self._session_factory)
        self._app = Application(api_urls + other_urls, session_factory=self._session_factory).listen(7777, '127.0.0.1')

    def run(self):
        tornado.ioloop.IOLoop.current().spawn_callback(self._updater.update_photos_of_next_user)
        # tornado.ioloop.IOLoop.current().spawn_callback(self._updater.tag_people)
        tornado.ioloop.IOLoop.current().start()


def main():
    ApmsServer().run()


if __name__ == '__main__':
    main()
