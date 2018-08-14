# -*- coding: utf-8 -*-
import time
import json
import logging
import asyncio
import aiohttp

from .api import PDApi

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class PDManager:
    """
    PDManager
    """

    def __init__(self, settings):
        self._info_fields = ','.join(settings['user_info_fields'])
        self._group_info_fields = ','.join(settings['group_info_fields'])
        self._api = PDApi(
            base=settings['base'],
            access_token=settings['token'],
            v=settings['version'],
            https=1,
            lang=settings['lang'])

    async def get_kind(self, screen_name):
        if screen_name.startswith('id'):
            try:
                _ = int(screen_name[2:])
                return 0  # user
            except ValueError:
                pass
        resp = await self._api.utils.resolveScreenName(screen_name=screen_name)
        log.debug(json.dumps(resp, indent=4))
        try:
            if resp['response']['type'] == 'user':
                return 0
            if resp['response']['type'] == 'group':
                return 1
        except KeyError:
            return None
        except TypeError:
            return 0

        return None

    async def get_user_info(self, user_id):
        resp = await self._api.users.get(user_ids=user_id, fields=self._info_fields, name_case='Nom')
        log.debug(json.dumps(resp, indent=4))
        return resp

    async def get_group_info(self, group_id):
        resp = await self._api.groups.getById(group_id=group_id, fields=self._group_info_fields)
        log.debug(json.dumps(resp, indent=4))
        return resp

    async def get_all_photos(self, user_id, albums_id=None):
        log.debug('get_all_photos id: {}. album_id: {}'.format(user_id, albums_id))
        params = {'owner_id': user_id, 'extended': 0, 'photo_sizes': 0, 'need_hidden': 1}

        if albums_id is not None:
            photos = []
            for album_id in albums_id.split(','):
                log.debug('Getting photos from album {}'.format(album_id))
                params['album_id'] = album_id
                photos.extend(await PDManager._get_all_items(self._api.photos.get, params))
            return photos

        return await PDManager._get_all_items(self._api.photos.getAll, params)

    async def get_user_photos(self, user_id):
        params = {'user_id': user_id, 'extended': 1, 'photo_sizes': 0, 'need_hidden': 1}
        return await PDManager._get_all_items(self._api.photos.getUserPhotos, params)

    async def get_albums(self, user_id):
        params = {'owner_id': user_id, 'need_system': 1}
        return await PDManager._get_all_items(self._api.photos.getAlbums, params)

    async def create_album(self, title, description):
        params = {'title': title, 'description': description, 'privacy_view': 'only_me', 'privacy_comment': 'only_me'}

        def get():
            return self._api.photos.createAlbum(params)

        resp = await PDManager.retry_if_failed(get, tries=3)

        return resp

    @staticmethod
    async def retry_if_failed(func, tries):
        for _ in range(tries):
            try:
                res = await func()
            except aiohttp.ClientError as ex:
                log.error('{} {}.   retrying'.format(type(ex), ex))
                await asyncio.sleep(5)
                continue  # retrying
            else:
                break
        else:
            raise Exception('Maximum retries number exceeded')
        return res

    @staticmethod
    async def _get_items(api_call, params, offset=0):

        async def get():
            try:
                offset_params = {'offset': offset, 'count': 200}
                myp = {**params, **offset_params}
                resp = await api_call(**myp)
                return resp['response']['items'], resp['response']['count']
            except Exception as ex:
                log.error('{} {} \n{}'.format(type(ex), ex, json.dumps(resp, indent=4)))
                raise

        return await PDManager.retry_if_failed(get, 4)

    @staticmethod
    async def _get_all_items(api_call, params):
        resp, count = [], 1
        while len(resp) < count:
            resp2, count = await PDManager._get_items(api_call, params, len(resp))
            log.info('Getting items {} of {}'.format(len(resp), count))
            resp.extend(resp2)
        return resp
