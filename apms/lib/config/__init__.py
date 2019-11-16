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
from pathlib import Path

import yaml

log = logging.getLogger("apms-config")  # pylint: disable=invalid-name
logging.basicConfig(
    format="%(asctime)s.%(msecs)-3d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%d-%m-%Y:%H:%M:%S",
    level="INFO",
)


class AmpsConfig:
    """
    Config
    """

    def __init__(self):
        self._config = {}

        self._static_dir = None
        self._photos_dir = None
        self._db_connection_string = None

    @staticmethod
    def default_config_file():
        apms_dir = Path(__file__).resolve().parent.parent.parent
        return apms_dir / "config.yml"

    def load_config(self, config_file):
        apms_dir = Path(__file__).resolve().parent.parent.parent
        log.info(f"Loading config from {config_file}")
        self._config = yaml.load(open(config_file, "r"))

        self._static_dir = Path(
            apms_dir / self._config["server"]["static_dir"]
        ).resolve()
        self._photos_dir = Path(
            apms_dir / self._config["server"]["photos_dir"]
        ).resolve()
        self._db_connection_string = self._config["server"]["db_connection_string"]
        log.info(f"Static dir: {self._static_dir}")
        log.info(f"Photos dir: {self._photos_dir}")

    @property
    def raw_data(self):
        return self._config

    @property
    def static_dir(self):
        return self._static_dir

    @property
    def photos_dir(self):
        return self._photos_dir

    @property
    def trash_dir(self):
        return "/tmp/apms/photos_to_delete"

    @property
    def db_connection_string(self):
        return self._db_connection_string


config = AmpsConfig()  # pylint: disable=invalid-name
