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

import os
import json
import logging

from tornado.ioloop import IOLoop
from tornado_sqlalchemy import make_session_factory, SessionMixin
from tornado.web import RequestHandler, Application, StaticFileHandler

from apms.lib.db.database import Photo, User, Album
from apms.lib.config import config

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
logging.getLogger('tornado').setLevel(logging.WARNING)


class PhotosHandler(RequestHandler, SessionMixin):

    def get(self, *args, **kwargs):
        page = int(self.get_query_argument('page', 1))
        limit = int(self.get_query_argument('limit', 50))
        offset = (page - 1) * limit
        owner_id = self.get_query_argument('owner_id', None)
        sort_by = self.get_query_argument('sort_by', None)
        missing = self.get_query_argument('missing', None)
        to_delete = self.get_query_argument('to_delete', None)
        foreign = self.get_query_argument('foreign', None)

        with self.make_session() as session:
            query = session.query(Photo).filter_by(deleted_by_me=(to_delete is not None))
            if owner_id:
                query = query.filter_by(owner_id=owner_id)

            count = query.count()
            result = query.order_by(Photo.date_downloaded.desc()).offset(offset).limit(limit).all()
            photos = {'count': count, 'photos': list(map(lambda photo: photo.to_json(), result))}
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(photos))


class MainHandler(RequestHandler):
    """
    Redirects to ui
    """

    def get(self, file_name='index.html'):  # pylint: disable=arguments-differ
        log.debug('MainHandler {}'.format(file_name))
        self.write(open(os.path.join(config.static_dir, 'index.html')).read())


class NonCachedStaticFileHandler(StaticFileHandler):

    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.set_header('Expires', '0')


class ApmsServer:

    def __init__(self):
        self._session_factory = make_session_factory(config.db_connection_string)
        self._app = Application(
            [
                (r"/api/photos", PhotosHandler),
                (r'/files/photos/(.*)', NonCachedStaticFileHandler, {
                    'path': config.photos_dir
                }),
                (r'/', MainHandler),
                (r'/(.*)', NonCachedStaticFileHandler, {
                    'path': config.static_dir
                }),
            ],
            session_factory=self._session_factory).listen(7777)

    def run(self):
        IOLoop.current().start()
