# -*- coding: utf-8 -*-
"""
Database test
"""
# pylint: disable=all
import json
import asyncio
import datetime
import logging
from pprint import pprint

from pytest import fixture

from faker import Faker

from tornado_sqlalchemy import make_session_factory, SessionMixin
from ..lib.db.database import Tag, User, Photo, Album, BASE

from sqlalchemy import Column, Integer, UnicodeText, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ..lib.providers.pd.pdmanager import PDManager
from ..lib.config import config

# pylint: disable=redefined-outer-name,missing-docstring

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
logging.basicConfig(
    format='%(asctime)s.%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    level='INFO')


def test_users_add(session_factory, fake_user_maker):
    user = fake_user_maker.make()
    pprint(user.to_json())
    with session_factory.make_session() as session:
        session.add(user)

    pprint(user.to_json())


def test_to_json(fake_user_maker):
    pprint(fake_user_maker.make().to_json())


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


def test_multiple_sessions(session_factory):
    with session_factory.make_session() as session:
        pass
