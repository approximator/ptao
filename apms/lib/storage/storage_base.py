# -*- coding: utf-8 -*-
"""
Storage base class
"""

import logging

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class StorageBase:
    """
    Base class for storage
    """

    def __init__(self):
        self._current_dir = ''

    def cd(self, dir_name):  # pylint: disable=invalid-name
        """Change directory"""
        self._current_dir = self.get_absolute_path(dir_name)

    @property
    def cwd(self):
        """Get current working directory"""
        return self._current_dir

    @staticmethod
    def is_absolute(path):
        """Check if path is absolute"""
        return path.startswith('/')

    def get_absolute_path(self, path):
        """Get absolute path for any give path"""
        abs_path = path if self.is_absolute(path) else self.cwd.rstrip('/') + '/' + path
        return abs_path.lstrip('/')
