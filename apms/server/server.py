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
import datetime

import tornado
from tornado.web import RequestHandler, Application, StaticFileHandler
from sqlalchemy.orm import joinedload
from sqlalchemy import not_
from tornado_sqlalchemy import make_session_factory, SessionMixin

from apms.lib.providers.pd.pdmanager import PDManager
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
        photos_of = self.get_query_argument('photos_of', None)
        photos_by = self.get_query_argument('photos_by', None)
        # sort_by = self.get_query_argument('sort_by', None)
        missing = self.get_query_argument('missing', None)
        to_delete = self.get_query_argument('to_delete', None)
        # foreign = self.get_query_argument('foreign', None)
        small = self.get_query_argument('small', None)
        photo_text = self.get_query_argument('photo_text', None)

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
                if photos_of is not None:
                    query = query.filter(Photo.people.any(User.id == photos_of))
                if photos_by is not None:
                    query = query.filter(Photo.authors.any(User.id == photos_by))
                if photo_text is not None:
                    query = query.filter(Photo.text.ilike(f'%{photo_text}%'))

                count = query.count()
                result = query.order_by(Photo.date_downloaded.desc()).offset(offset).limit(limit).all()

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
            users = {'users': [user.to_json() for user in session.query(User).all()]}
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(users))


async def get_user_from_remote(user_id):
    mgr = PDManager(config.raw_data['api_clients'])
    log.info(f'Getting user info: {user_id}')
    info = None
    kind = await mgr.get_kind(user_id)
    log.debug(f'Kind: {kind}')

    if kind == 0:
        info = await mgr.get_user_info(user_id)
    if kind == 1:
        info = await mgr.get_group_info(user_id)
    log.debug(json.dumps(info, indent=4))

    if info is None:
        return None

    if 'error' in info:
        log.error(json.dumps(info, indent=4))
        return None

    info = info['response'][0]
    info['kind'] = kind
    info['first_name'] = info['first_name'] if kind == 0 else info['name']
    info['last_name'] = info['last_name'] if kind == 0 else 'group'
    info['date_added'] = datetime.datetime.now()
    info['date_info_updated'] = datetime.datetime.now()
    info['url'] = f'{config.raw_data["api_clients"].get("host_url_base", "")}/{info["domain"]}' if kind == 0 else info[
        'screen_name']
    info['photo'] = info['photo_max_orig'] if kind == 0 else info['photo_200']
    info['nick_name'] = info.get('nickname', '')
    info['city'] = info.get('city', {}).get('title', '')
    info['status_str'] = info.get('status', '') if kind == 0 else info.get('description', '')

    usr_fields = [fld_name for fld_name, fld_type in User.__dict__.items() if str(fld_type).startswith('User')]
    info = {key: val for key, val in info.items() if key in usr_fields and str(val)}
    return User(**info)


class PeopleTagHandler(RequestHandler, SessionMixin):

    async def put(self, *args, **kwargs):
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
            log.info([user.to_json() for user in people])
            for photo in session.query(Photo).filter(Photo.id.in_(photos_ids)).all():
                if not overwrite_tags:
                    people.extend(photo.people)
                    photo.people = list(set(people))  # remove duplicates
                else:
                    log.info('Overwriting tags')
                    photo.people = people
            session.commit()
        self.write(json.dumps({'result': 'Success'}))


class UsersUpdateHandler(RequestHandler, SessionMixin):

    async def get_user_info(self, user_id):
        user = await get_user_from_remote(user_id)
        user_info = user.to_json()
        user_info['host_url'] = user_info['url']
        log.debug(json.dumps(user_info, indent=4))

        with self.make_session() as session:
            local_user = session.query(User).filter(User.id == user_info['id']).all()
            if local_user:
                log.info(f'User {user.first_name} {user.last_name} exists in the DB')
                user_info['local_id'] = local_user.id
                user_info['local_photos_url'] = f'/photos?owner_id={local_user.id}'

        return user, user_info

    async def get(self, user_id):  # pylint: disable=arguments-differ
        try:
            _, user_info = await self.get_user_info(user_id)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(user_info))
        except Exception as ex:  # pylint: disable=broad-except
            log.error(f'Can not get information about {user_id} ({ex})')
            self.set_status(400)
            self.write(json.dumps({'result': 'Error', 'cause': 'Wrong request', 'description': str(ex)}))
            return

    async def put(self, user_id):  # pylint: disable=arguments-differ
        try:
            user, _ = await self.get_user_info(user_id)

            with self.make_session() as session:
                session.add(user)

            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps({'result': 'Success'}))
        except Exception as ex:  # pylint: disable=broad-except
            log.error(f'Can not get information about {user_id} ({ex})')
            self.set_status(400)
            self.write(json.dumps({'result': 'Error', 'cause': 'Wrong request', 'description': str(ex)}))
            return


class ApmsServer:

    def __init__(self, config_file=None):
        config.load_config(config_file if config_file is not None else config.default_config_file())
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
        # tornado.ioloop.IOLoop.current().spawn_callback(self._updater.tag_people)
        tornado.ioloop.IOLoop.current().start()
