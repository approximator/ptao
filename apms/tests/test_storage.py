# -*- coding: utf-8 -*-
"""
Storage test
"""
# pylint: disable=all
# pylint: disable=redefined-outer-name,missing-docstring

# from pytest import fixture

# from ..lib.storage.s3.s3_storage import S3Storage

# @fixture
# def storage():
#     import yaml
#     storage_config = yaml.load(open('../settings.bak.yml'))['storage']
#     del storage_config['base_dir']
#     return S3Storage(**storage_config)

# def test_cd(storage):
#     assert storage.cwd == ''

#     storage.cd('some_dir')
#     assert storage.cwd == 'some_dir'

#     storage.cd('some_other_dir')
#     assert storage.cwd == 'some_dir/some_other_dir'

# def test_get_absolute(storage):
#     assert storage.get_absolute_path('file_name') == 'file_name'
#     assert storage.get_absolute_path('/dir_name/file_name') == 'dir_name/file_name'
#     storage.cd('some-dir')
#     assert storage.get_absolute_path('/dir_name/file_name') == 'dir_name/file_name'
#     assert storage.get_absolute_path('file_name') == 'some-dir/file_name'
