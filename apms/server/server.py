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
import shutil
import logging

import tornado
from tornado.web import RequestHandler, Application, StaticFileHandler
from sqlalchemy.orm import joinedload
from sqlalchemy import not_
from tornado_sqlalchemy import make_session_factory, SessionMixin

from apms.lib.db.database import Photo, User
from apms.lib.config import config
from .updater import Updater

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
logging.getLogger('tornado').setLevel(logging.WARNING)

# pylint: disable=abstract-method


class PhotosHandler(RequestHandler, SessionMixin):
    """
    Handler for API methods of photos functions
    """

    def get(self, *args, **kwargs):  # pylint: disable=too-many-locals
        page = int(self.get_query_argument('page', 1))
        limit = int(self.get_query_argument('elements_per_page', 200))
        offset = (page - 1) * limit
        owner_id = self.get_query_argument('owner_id', None)
        # sort_by = self.get_query_argument('sort_by', None)
        missing = self.get_query_argument('missing', None)
        to_delete = self.get_query_argument('to_delete', None)
        # foreign = self.get_query_argument('foreign', None)
        small = self.get_query_argument('small', None)

        with self.make_session() as session:
            if to_delete is not None:
                count, result = PhotosHandler.get_photos_to_delete(session)
            elif missing is not None:
                count, result = PhotosHandler.get_missing_photos(session)
            else:
                query = session.query(Photo).options(joinedload(Photo.owner)).filter(not_(Photo.deleted_by_me))
                if owner_id:
                    query = query.filter_by(owner_id=owner_id)
                if small:
                    query = query.filter(Photo.width < 450)

                count = query.count()
                result = query.order_by(Photo.date_added.desc()).offset(offset).limit(limit).all()

            photos = {'count': count, 'photos': list(map(lambda photo: photo.to_json(), result))}
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(photos))

    @staticmethod
    def get_missing_photos(session):
        query = session.query(Photo).options(joinedload(Photo.owner)).filter_by(deleted_by_me=False)
        result = list(
            filter(lambda photo: not os.path.exists(os.path.join(config.photos_dir, photo.dir_name, photo.file_name)),
                   query.order_by(Photo.date_added.desc()).all()))
        return len(result), result[0:200]

    @staticmethod
    def get_photos_to_delete(session):
        query = session.query(Photo).options(joinedload(Photo.owner)).filter_by(deleted_by_me=True)
        result = list(
            filter(lambda photo: os.path.exists(os.path.join(config.photos_dir, photo.dir_name, photo.file_name)),
                   query.order_by(Photo.date_downloaded.desc()).all()))
        return len(result), result

    def delete(self, *args, **kwargs):
        try:
            photos_to_delete = json.loads(self.request.body.decode())['photos']
        except Exception as ex:  # pylint: disable=broad-except
            log.info(ex)
            self.set_status(400)
            self.write(json.dumps({'result': 'Error', 'cause': 'Wrong request', 'description': str(ex)}))
            return

        log.info('Going to remove {}'.format(photos_to_delete))
        with self.make_session() as session:
            query = session.query(Photo).filter(Photo.id.in_(photos_to_delete))
            count = query.count()
            if not count:
                self.set_status(404)
                self.write(json.dumps({'result': 'Error', 'cause': 'Not Found'}))
                return
            for photo in query.all():
                if not os.path.isdir(config.trash_dir):
                    os.makedirs(config.trash_dir)

                photo.deleted_by_me = True
                fname = os.path.join(config.photos_dir, photo.dir_name, photo.file_name)
                new_fname = os.path.join(config.trash_dir, photo.file_name)
                log.info('Moving {} -> {}'.format(fname, new_fname))
                try:
                    shutil.move(fname, new_fname)
                except OSError:
                    log.exception('Cannot move {} -> {}'.format(fname, new_fname))
                log.info('{} marked as deleted by me'.format(photo.id))
            session.commit()

            self.write(json.dumps({'result': 'Ok', 'deleted': photos_to_delete}))


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


class UsersHandler(RequestHandler, SessionMixin):

    def get(self, *args, **kwargs):
        with self.make_session() as session:
            users = {
                'users':
                list(
                    map(lambda user: user.to_json(),
                        session.query(User).order_by(User.date_photos_updated_successfully).all()))
            }
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(users))




class PeopleTagHandler(RequestHandler, SessionMixin):

    async def put(self):
        try:
            params = json.loads(self.request.body.decode())
            log.info(json.dumps(params, indent=4))
            overwrite_tags = bool(params.get('overwriteTags', False))
            people_ids = list(map(int, params['people']))
            photos_ids = list(map(int, params['photos']))
        except Exception as ex:  # pylint: disable=broad-except
            log.info(ex)
            self.set_status(400)
            self.write(json.dumps({'result': 'Error', 'cause': 'Wrong request', 'description': str(ex)}))
            return

        with self.make_session() as session:
            people = session.query(User).filter(User.id.in_(people_ids)).all()
            log.info(list(map(lambda user: user.to_json(), people)))
            for photo in session.query(Photo).filter(Photo.id.in_(photos_ids)).all():
                if not overwrite_tags:
                    people.extend(photo.peoples)
                    photo.peoples = list(set(people))  # remove duplicates
                else:
                    log.info('Overwriting tags')
                    photo.peoples = people
            session.commit()
        self.write(json.dumps({'result': 'Success'}))
class ApmsServer:

    def __init__(self):
        self._session_factory = make_session_factory(config.db_connection_string)
        self._updater = Updater(config, self._session_factory)
        self._app = Application([
            (r"/api/photos", PhotosHandler),
            (r"/api/photos/tagPeople", PeopleTagHandler),
            (r"/api/users/(.+)/update", UsersUpdateHandler),
            (r"/api/users", UsersHandler),
            (r'/photos(.*)', MainHandler),
            (r'/people(.*)', MainHandler),
            (r'/files/photos/(.*)', NonCachedStaticFileHandler, {
                'path': config.photos_dir
            }),
            (r'/', MainHandler),
            (r'/(.*)', NonCachedStaticFileHandler, {
                'path': config.static_dir
            }),
        ],
                                session_factory=self._session_factory).listen(7777, '127.0.0.1')

    def run(self):
        tornado.ioloop.IOLoop.current().spawn_callback(self._updater.update_photos_of_next_user)
        tornado.ioloop.IOLoop.current().start()
