"""
Copyright © 2019 Approximator. All rights reserverd.
Author: Approximator (alex@nls.la)
"""
import os
import yaml
import time
import shutil
import random
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from faker import Faker
from pytest import fixture
from tornado_sqlalchemy import make_session_factory, SessionMixin
from apms.lib.db.database import BASE, User, Photo
from apms.lib.config import config

from PIL import Image, ImageFilter

# pylint: disable=too-few-public-methods,invalid-name,redefined-outer-name
fake = Faker("en_US")


@fixture
def image_maker(test_config):
    class Maker:
        def __init__(self):
            self._current_photo_id = 0
            self._photos = []
            self._photos_dir = Path(
                yaml.load(open(test_config, "r"))["server"]["photos_dir"]
            )

        def make(self, width=200, height=200):
            self._current_photo_id += 1
            image_file = f"photo_{self._current_photo_id}.png"

            photo = Photo(
                origin_id=self._current_photo_id,
                width=width,
                height=height,
                url=fake.url(),
                dir_name="",
                file_name=image_file,
                date_added=fake.date_time(),
                date_downloaded=datetime.datetime.now(),
                text=fake.catch_phrase(),
            )
            self._photos.append(photo)
            return photo

        def generate_image(self, photo):
            img = Image.new("L", [photo.width, photo.height], 255)
            data = img.load()

            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    data[x, y] = random.randint(1, 255)
            img = img.filter(filter=ImageFilter.BLUR)
            img.save(self._photos_dir / photo.file_name)
            return self._photos_dir / photo.file_name

        def save(self):
            print("Generating images")
            start_time = time.time()
            with ThreadPoolExecutor() as executor:
                result = list(executor.map(self.generate_image, self._photos))
            print(
                f"Generated {len(result)} images. Took {int(time.time() - start_time)} sec."
            )

    return Maker()


class AppHandler(SessionMixin):
    """
    This class mimics tornado's RequestHandler
    Needed only for convenient session_factory and SessionMixin usage
    """

    class App:
        def __init__(self, db_connection_string):
            self._session_factory = make_session_factory(db_connection_string)
            self.settings = {"session_factory": self._session_factory}
            BASE.metadata.create_all(self._session_factory.engine)

    def __init__(self, db_connection_string):
        self.application = AppHandler.App(db_connection_string)


@fixture(scope="module")  # will be called once for the entire test module
def session_factory(test_config):
    config.load_config(test_config)
    yield AppHandler(config.db_connection_string)


@fixture(scope="module")
def test_config(tmpdir_factory):
    temp_dir = Path(tmpdir_factory.mktemp("apms-test-data"))
    config_filename = temp_dir / "config.yml"
    db_filename = temp_dir / "db.sqlite"
    static_dir = temp_dir / "build"
    photos_dir = temp_dir / "photos"

    shutil.copytree("../apms-ui/build", static_dir)

    config_data = {
        "server": {
            "db_connection_string": f"sqlite:////{db_filename}",
            "static_dir": static_dir,
            "photos_dir": f"{photos_dir}",
        },
        "updater": {"pause": True},
        "api_clients": {
            "base": "http://127.0.0.1/method",
            "version": "5.71",
            "lang": "en",
            "token": "aaa",
            "user": 111,
            "user_info_fields": ["first_name", "last_name", "about",],
            "group_info_fields": ["city", "contacts",],
            "host_url_base": "http://127.0.0.1",
        },
    }

    print(f"Creating test config: {config_filename}")
    photos_dir.mkdir(parents=True)
    yaml.dump(config_data, open(config_filename, "w"))
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
                status_str=fake.catch_phrase(),
            )

    return Maker
