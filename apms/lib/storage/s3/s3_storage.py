# -*- coding: utf-8 -*-
"""
S3Storage
"""

import logging

import boto3
from botocore.errorfactory import ClientError

from ..storage_base import StorageBase

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class S3Storage(StorageBase):
    """
    S3 storage
    """

    def __init__(self, region_name, endpoint_url, access_key_id, secret_access_key, bucket):
        super().__init__()
        self._bucket = bucket
        self._session = boto3.session.Session()
        self._client = self._session.client(
            's3',
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key)

    def exists(self, file_name):
        """Check if file exists in the storage"""
        full_file_path = self.get_absolute_path(file_name)
        log.debug('checking {}'.format(full_file_path))
        try:
            self._client.head_object(Bucket=self._bucket, Key=full_file_path)
            return True
        except ClientError as ex:
            log.error('{} not exists ({}: {})'.format(full_file_path, type(ex), ex))
            return False

    def store(self, local_file, file_name):
        """Store file in the storage"""
        full_file_path = self.get_absolute_path(file_name)
        log.debug('uploading {}'.format(full_file_path))
        self._client.upload_file(
            local_file,  # Path to local file
            self._bucket,  # Name of Space
            self.get_absolute_path(file_name)  # Name for remote file
        )
        # S3UploadFailedError

    def get_all(self):
        """Get a list of all keys in a bucket."""
        keys = []

        paginator = self._client.get_paginator('list_objects')
        pages = paginator.paginate(Bucket=self._bucket)
        for page in pages:
            for obj in page['Contents']:
                keys.append(obj['Key'])
        return keys
