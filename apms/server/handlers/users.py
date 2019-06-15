import datetime
import json
import logging

from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin

from apms.lib.config import config
from apms.lib.db.database import User
from apms.lib.providers.pd.pdmanager import PDManager

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class UsersHandler(RequestHandler, SessionMixin):

    def get(self):
        """Get people
        ---
        summary: Get people
        tags:
          - "People"

        responses:
          200:
            description: List of people
            schema: GetUsersResponseSchema
        """
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
        """Get user info
        ---
        summary: Get user info
        tags:
          - "People"

        responses:
          200:
            description: Information about user
            schema: GetUserResponseSchema
        """
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
        """Update user info
        ---
        summary: Update user info
        tags:
          - "People"

        parameters:
          - name: user_id
            in: path
            type: string
            required: true

        responses:
          200:
            description: Information about user
            schema: GetUserResponseSchema
        """
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
