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
import logging
import asyncio
import datetime

import aiofiles
import aiohttp

from PIL import Image
from sqlalchemy import or_, and_, not_

from ..lib.db.database import Photo, User
from ..lib.providers.pd.pdmanager import PDManager

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Updater:
    """
    Updater
    """

    def __init__(self, config, session_factory):
        self._config = config
        self._session_factory = session_factory
        self._photos_dir = config.photos_dir

    def get_photo_size(self, photo):
        dirname = os.path.join(self._photos_dir, photo.dir_name)
        filename = os.path.join(dirname, photo.file_name)
        if not os.path.exists(filename):
            log.info('File {} does not exists'.format(filename))
            photo_size = 100, 100
        else:
            try:
                photo_size = Image.open(filename).size
            except Exception as ex:  # pylint: disable=broad-except
                log.error('{}: {}'.format(type(ex), ex))
                photo_size = 100, 100

        log.info('Size of photo {}: {}'.format(filename, photo_size))
        return photo_size

    async def download_photo(self, photo, url):
        try:
            dirname = os.path.join(self._photos_dir, photo.dir_name)
            filename = os.path.join(dirname, photo.file_name)

            if os.path.exists(filename):
                log.warning('File exists: {}'.format(filename))
                return

            if not os.path.exists(dirname):
                log.info('Making directory')
                os.makedirs(dirname)
        except Exception as ex:  # pylint: disable=broad-except
            log.error('{}: {}.  Photo: {}'.format(type(ex), ex, photo))
            raise

        log.info('Downloading {} to {}'.format(url, filename))

        async def download():
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
                    async with aiofiles.open(filename, 'wb') as photo_file:
                        await photo_file.write(data)

        await PDManager.retry_if_failed(download, 20)

    @staticmethod
    def get_photo_url(info):  # pylint: disable=too-many-return-statements
        if info.get('photo_2560', None) is not None:
            return info['photo_2560']

        if info.get('photo_1280', None) is not None:
            return info['photo_1280']

        if info.get('photo_807', None) is not None:
            return info['photo_807']

        if info.get('photo_604', None) is not None:
            return info['photo_604']

        if info.get('photo_130', None) is not None:
            return info['photo_130']

        if info.get('photo_75', None) is not None:
            return info['photo_75']

        return None

    async def update_photos_of_next_user(self):
        while True:
            await asyncio.sleep(10)
            log.info('Updating photos of next user')
            onedayearly = datetime.timedelta(hours=8)
            since = datetime.datetime.now() - onedayearly

            session = self._session_factory.make_session()
            user = session.query(User).filter(
                and_(or_(User.date_photos_updated < since, User.date_photos_updated == None),
                     not_(User.pause_update))).order_by(  # pylint: disable=singleton-comparison
                         User.date_photos_updated).first()

            if user is None:
                log.info('No users to update')
                continue

            await self.update_photos_of(user, session)

    async def update_photos_of(self, user, db_session):
        log.info('Going to update {} {}'.format(user.first_name, user.last_name))
        log.info('Was updated {} minutes ago'.format(datetime.datetime.now() -
                                                     user.date_photos_updated if user.date_photos_updated else 'never'))

        await self.add_new_photos(user, db_session)

    @staticmethod
    def photo_from_json(info):
        return Photo(
            origin_id=info['id'],
            url=Updater.get_photo_url(info),
            dir_name='{}'.format(info['owner_id']),
            file_name=Updater.get_photo_url(info).split('/')[-1],
            date_downloaded=datetime.datetime.now(),
            owner_id=info['owner_id'],
            date_added=datetime.datetime.fromtimestamp(int(info['date'])),
            width=info.get('width', 0),
            height=info.get('height', 0),
            text=info['text'])

    def tag_people(self):
        log.info('Start tag_people')
        session = self._session_factory.make_session()
        for user in session.query(User).filter(User.owner_is_on_photos).all():
            log.info(f'Tag photos of {user.first_name} {user.last_name}')
            for photo in user.photos:
                people = [user]
                people.extend(photo.peoples)
                photo.peoples = list(set(people))
        session.commit()

    async def add_new_photos(self, user, db_session):
        log.info('Starting photos updating')

        pd_manager = PDManager(self._config.raw_data['api_clients'])

        user.date_photos_updated = datetime.datetime.now()
        db_session.commit()

        log.info('Filter by albums {}'.format(user.filter_by_albums))

        try:
            resp = []
            log.debug('Analysing photos of {}'.format(user.url))
            try:
                resp = await pd_manager.get_all_photos(user.id if user.kind == 0 else -user.id, user.filter_by_albums)
            except Exception as ex:  # pylint: disable=broad-except
                log.error('Can not get photos of {}. {}: {}'.format(user.url, type(ex), ex))
                return

            # json.dump(resp, open('/tmp/resp.json', 'w'))

            new_photo_ids = set(map(lambda info: info['id'], resp)) - set(
                map(lambda photo: photo.origin_id, user.photos))
            new_photos = list(
                map(Updater.photo_from_json, filter(lambda ph_info: ph_info['id'] in new_photo_ids, resp)))
            new_photos_count = len(new_photos)
            log.info('New photos: {}'.format(new_photos_count))
            downloaded = 0
            for new_photo in new_photos:
                new_photo.owner_id = user.id
                downloaded += 1
                log.info('Downloading photo {} of {}'.format(downloaded, new_photos_count))
                await self.download_photo(new_photo, new_photo.url)
                if new_photo.width == 0:
                    new_photo.width, new_photo.height = self.get_photo_size(new_photo)
                if user.owner_is_on_photos:
                    new_photo.peoples = user
                db_session.add(new_photo)
                if downloaded % 100 == 0:
                    db_session.commit()

                    # dirname = os.path.join(PHOTOS_BASE_DIR, new_photo.dir_name)
                    # filename = os.path.join(dirname, new_photo.file_name)
                    # try:
                    #     app.pageduck_exif.add_keyword(filename, '{} {}'.format(
                    #         user.first_name, user.last_name))
                    #     app.pageduck_exif.set_comment(filename, new_photo.text)
                    #     app.pageduck_exif.set_date(filename, new_photo.date_added)
                    # except Exception as ex:
                    #     log.error('Exception: {}'.format(ex))

        except Exception as ex:  # pylint: disable=broad-except
            log.error('Error while processing new photos {}'.format(ex))

        user.date_photos_updated_successfully = datetime.datetime.now()
        db_session.commit()
        log.info('Photos updating done')
