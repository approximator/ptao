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

from dataclasses import field
from typing import List, ClassVar, Type

import marshmallow_dataclass
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import ModelSchema

from ..lib.db.database import Tag, Album, User, Photo


@marshmallow_dataclass.dataclass
class PeopleTagRequest:
    photos: List[int]
    people: List[int]
    authors: List[int]
    overwrite_people_tags: bool = field(metadata={'required': False}, default=False)
    overwrite_authors_tags: bool = field(metadata={'required': False}, default=False)
    Schema: ClassVar[Type[Schema]] = Schema


@marshmallow_dataclass.dataclass
class DeletePhotosRequest:
    photos: List[int]
    Schema: ClassVar[Type[Schema]] = Schema


@marshmallow_dataclass.dataclass
class ApiResult:
    result: str
    message: str
    Schema: ClassVar[Type[Schema]] = Schema


class TagSchema(ModelSchema):

    class Meta:
        model = Tag


class AlbumSchema(ModelSchema):

    class Meta:
        model = Album


class UserSchema(ModelSchema):

    class Meta:
        model = User


class PhotoSchema(ModelSchema):

    class Meta:
        model = Photo


class GetPhotosResponseSchema(ApiResult.Schema):
    photos = fields.Nested(PhotoSchema, many=True)


class GetUsersResponseSchema(ApiResult.Schema):
    users = fields.Nested(UserSchema, many=True)


class GetUserResponseSchema(ApiResult.Schema):
    user = fields.Nested(UserSchema)
