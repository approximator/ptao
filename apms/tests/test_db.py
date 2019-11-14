# -*- coding: utf-8 -*-
"""
Database test
"""
# pylint: disable=all
import json
import asyncio
import logging
import concurrent
from pprint import pprint

import pytest

from apms.lib.db.database import Tag, User, Photo, Album, BASE

from apms.lib.providers.pd.pdmanager import PDManager
from apms.lib.config import config

log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s.%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%d-%m-%Y:%H:%M:%S",
    level="INFO",
)


def test_users_add(session_factory, fake_user_maker):
    user = fake_user_maker.make()
    pprint(user.to_json())
    with session_factory.make_session() as session:
        session.add(user)

    pprint(user.to_json())


def test_to_json(fake_user_maker):
    pprint(fake_user_maker.make().to_json())


@pytest.mark.skip("Test data needs to be prepared")
def test_from_json():
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    user_id = "someuser"

    async def run_test():
        user = await get_user_from_remote(user_id)
        print(json.dumps(user.to_json(), indent=4))

    coro = asyncio.coroutine(run_test)
    event_loop.run_until_complete(coro())
    event_loop.close()


@pytest.mark.skip("Fix later")
def test_get_tags():
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    config.load_config(config.default_config_file())
    pdm = PDManager(config.raw_data["api_clients"])

    async def run_test():
        user = await pdm.get_tags("id1", "id2")
        print(json.dumps(user, indent=4))

    coro = asyncio.coroutine(run_test)
    event_loop.run_until_complete(coro())
    event_loop.close()


def test_multiple_sessions(session_factory, fake_user_maker):
    event_loop = asyncio.get_event_loop()
    with session_factory.make_session() as outer_session:
        outer_session.add(fake_user_maker.make())
        outer_session.commit()
        for usr in outer_session.query(User).order_by(User.date_added.desc()).all():
            print("  -  ", usr.first_name, usr.last_name)

        def session1():
            with session_factory.make_session() as session:
                users = [fake_user_maker.make() for _ in range(10)]
                for user in users:
                    print(f"[coro1] Adding {user.first_name}")
                    session.add(user)
                session.commit()
                return len(users)

        def session2():
            with session_factory.make_session() as session:
                users = [fake_user_maker.make() for _ in range(10)]
                for user in users:
                    print(f"[coro2] Adding {user.first_name}")
                    session.add(user)
                session.commit()
                return len(users)

        async def go():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return await asyncio.wait(
                    [
                        event_loop.run_in_executor(pool, session1),
                        event_loop.run_in_executor(pool, session2),
                    ],
                    loop=event_loop,
                )

        event_loop.run_until_complete(go())
    print("Done")
