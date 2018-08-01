# -*- coding: utf-8 -*-
import logging

import aiohttp

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class PDApi:  # pylint: disable=too-few-public-methods
    """
    Api
    """

    def __init__(self, base, **common_arguments):
        self._base = base
        self._common_arguments = common_arguments

    def __getattr__(self, item):
        return PDMethod(item, self._base, **self._common_arguments)


class PDMethod:  # pylint: disable=too-few-public-methods
    """
    API method
    """

    def __init__(self, method_name, base, **common_arguments):
        self._base = base
        self._name = method_name
        self._common_arguments = common_arguments

    def __getattr__(self, item):
        return PDMethod('{}.{}'.format(self._name, item), self._base, **self._common_arguments)

    async def __call__(self, **method_args):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    '{}/{}'.format(self._base, self._name), params={
                        **method_args,
                        **self._common_arguments
                    }, timeout=5) as resp:
                return await resp.json()
