# -*- coding: utf-8 -*-
"""
Database test
"""
# pylint: disable=all
import json
import asyncio
import datetime
import logging

from pytest import fixture

from tornado_sqlalchemy import make_session_factory, SessionMixin
from ..lib.db.database import Tag, User, Photo, Album, BASE

from sqlalchemy import Column, Integer, UnicodeText, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ..lib.providers.pd.pdmanager import PDManager
from ..lib.config import config

# pylint: disable=redefined-outer-name,missing-docstring

session_factory = make_session_factory('sqlite:////tmp/test.sqlite')
BASE.metadata.create_all(session_factory.engine)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
logging.basicConfig(
    format='%(asctime)s.%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level='INFO')


class AppHandler(SessionMixin):

    class App:

        def __init__(self):
            self.settings = {'session_factory': session_factory}

    def __init__(self):
        self.application = AppHandler.App()


@fixture
def test_session_factory():
    return AppHandler()


@fixture
def some_user():
    return User(
        first_name='Fn',
        last_name='Lm',
        url='url',
        date_added=datetime.datetime.now(),
        date_info_updated=datetime.datetime.now())


def test_users_add(test_session_factory):
    session = session_factory.make_session()
    user = User(
        first_name='Fn',
        last_name='Lm',
        url='url',
        date_added=datetime.datetime.now(),
        date_info_updated=datetime.datetime.now())
    session.add(user)
    session.commit()


def test_to_json(some_user):
    print(some_user.to_json())


# def test_from_json():
#     event_loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(event_loop)

#     user_id = 'someuser'

#     async def run_test():
#         user = await get_user_from_remote(user_id)
#         print(json.dumps(user.to_json(), indent=4))

#     coro = asyncio.coroutine(run_test)
#     event_loop.run_until_complete(coro())
#     event_loop.close()


def test_multiple_sessions(test_session_factory):
    with test_session_factory.make_session() as session:
        pass
