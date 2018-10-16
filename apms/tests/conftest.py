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
import datetime
import yaml

from faker import Faker
from pytest import fixture
from tornado_sqlalchemy import make_session_factory, SessionMixin
from ..lib.db.database import BASE, User
from ..lib.config import config

# pylint: disable=too-few-public-methods,invalid-name,redefined-outer-name
fake = Faker('en_US')


class AppHandler(SessionMixin):
    """
    This class mimics tornado's RequestHandler
    Needed only for convenient session_factory and SessionMixin usage
    """

    class App:

        def __init__(self, db_connection_string):
            self._session_factory = make_session_factory(db_connection_string)
            self.settings = {'session_factory': self._session_factory}
            BASE.metadata.create_all(self._session_factory.engine)

    def __init__(self, db_connection_string):
        self.application = AppHandler.App(db_connection_string)


@fixture(scope="module")  # will be called once for the entire test module
def session_factory(test_config):
    config.load_config(test_config)
    yield AppHandler(config.db_connection_string)


@fixture(scope="module")
def test_config(tmpdir_factory):
    temp_dir = tmpdir_factory.mktemp("apms-test-data")
    config_filename = os.path.join(temp_dir, "config.yml")
    db_filename = os.path.join(temp_dir, "db.sqlite")
    photos_dir = os.path.join(temp_dir, "photos")

    config_data = {
        'server': {
            'db_connection_string': f'sqlite:////{db_filename}',
            'static_dir': '../apms-ui/build',
            'photos_dir': f'{photos_dir}'
        },
        'api_clients': {
            'base':
            'http://127.0.0.1/method',
            'version':
            '5.71',
            'lang':
            'ru',
            'token':
            'aaa',
            'user':
            111,
            'user_info_fields': [
                'first_name', 'last_name', 'verified', 'sex', 'bdate', 'city', 'country', 'home_town', 'has_photo',
                'photo_max_orig', 'domain', 'has_mobile', 'contacts', 'site', 'status', 'nickname', 'about'
            ],
            'group_info_fields': ['city', 'contacts', 'counters', 'country', 'description', 'main_album_id'],
            'host_url_base':
            'http://127.0.0.1'
        }
    }

    print(f'Creating test config: {config_filename}')
    yaml.dump(config_data, open(config_filename, 'w'))
    return config_filename


# pylint: disable=no-member
@fixture
def fake_user_maker():

    class Maker:

        @classmethod
        def make(cls):
            return User(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                url=fake.url(),
                date_added=fake.date_time(),
                date_info_updated=datetime.datetime.now(),
                status_str=fake.catch_phrase())

    return Maker
