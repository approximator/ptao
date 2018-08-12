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

from time import mktime

from sqlalchemy import Column, Integer, UnicodeText, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from tornado_sqlalchemy import declarative_base

# import logging
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# pylint: disable=too-many-instance-attributes,too-few-public-methods,invalid-name

BASE = declarative_base()

photos_tags = Table('__photos_tags__', BASE.metadata, Column('photo_id', ForeignKey('photos.id'), primary_key=True),
                    Column('tag_id', ForeignKey('tags.id'), primary_key=True))

photos_people = Table('__photos_people__', BASE.metadata, Column('photo_id', ForeignKey('photos.id'), primary_key=True),
                      Column('user_id', ForeignKey('users.id'), primary_key=True))

photos_albums = Table('__photos_albums__', BASE.metadata, Column('photo_id', ForeignKey('photos.id'), primary_key=True),
                      Column('album_id', ForeignKey('albums.id'), primary_key=True))


def to_unit_timestamp(date_time):
    if not date_time:
        return 0
    return int(mktime(date_time.timetuple()))


def obj_to_json(obj):
    data = obj.__dict__.copy()
    del data['_sa_instance_state']
    for key, _ in data.items():
        if key.startswith('date'):
            data[key] = to_unit_timestamp(data[key])
    return data


class Settings(BASE):
    __tablename__ = 'status_and_settings'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    pause_update = Column(Boolean(), nullable=False, default=False)


class Tag(BASE):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    slug = Column(UnicodeText(), nullable=False, unique=True)
    title = Column(UnicodeText(), nullable=False, unique=True)

    photos = relationship('Photo', secondary=photos_tags, back_populates='tags')

    def to_json(self):
        return {'id': self.id, 'slug': self.slug, 'title': self.title}


class Album(BASE):
    __tablename__ = 'albums'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    origin_id = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    title = Column(UnicodeText(), nullable=False)
    description = Column(UnicodeText(), nullable=False)
    rating = Column(Integer, nullable=False, default=0)

    owner = relationship("User", back_populates="albums")
    photos = relationship('Photo', secondary=photos_albums, back_populates='albums')

    def to_json(self):
        return obj_to_json(self)


class Photo(BASE):
    __tablename__ = 'photos'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="photos")

    peoples = relationship('User', secondary=photos_people, back_populates='photos_of')
    tags = relationship('Tag', secondary=photos_tags, back_populates='photos')
    albums = relationship('Album', secondary=photos_albums, back_populates='photos')

    origin_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False, default=0)
    url = Column(UnicodeText(), nullable=False)
    dir_name = Column(UnicodeText(), nullable=False)
    file_name = Column(UnicodeText(), nullable=False)
    new = Column(Boolean(), nullable=False, default=True)
    date_downloaded = Column(DateTime(), nullable=False)
    date_info_updated = Column(DateTime(), nullable=True)
    date_info_updated_successfully = Column(DateTime(), nullable=True)
    deleted = Column(Boolean(), nullable=False, default=False)
    deleted_by_me = Column(Boolean(), nullable=False, default=False)
    updating = Column(Boolean(), nullable=False, default=False)
    updating_interval = Column(Integer, nullable=False, default=60)

    date_added = Column(DateTime(), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    text = Column(UnicodeText(), nullable=True)

    def to_json(self):
        data = obj_to_json(self)
        data['local_url'] = '/files/photos/' + self.dir_name + '/' + self.file_name
        data['owner'] = self.owner.to_json() if self.owner else {}
        data['people'] = list(map(lambda user: user.to_json(), self.peoples)) if self.peoples else []
        return data


class User(BASE):
    __tablename__ = 'users'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    kind = Column(Integer, nullable=False, default=0)  # 0 - user, 1 - group
    first_name = Column(UnicodeText(), nullable=False, default='')
    last_name = Column(UnicodeText(), nullable=False, default='')
    domain = Column(UnicodeText(), nullable=True)
    nick_name = Column(UnicodeText(), nullable=True, default='')
    site = Column(UnicodeText(), nullable=True)
    status_str = Column(UnicodeText(), nullable=True)
    about = Column(UnicodeText(), nullable=True)
    date_birthday = Column(DateTime(), nullable=True)
    city = Column(UnicodeText(), nullable=True)
    date_added = Column(DateTime(), nullable=False)
    date_info_updated = Column(DateTime(), nullable=True)
    date_photos_updated = Column(DateTime(), nullable=True)
    date_info_updated_successfully = Column(DateTime(), nullable=True)
    date_photos_updated_successfully = Column(DateTime(), nullable=True)
    deleted = Column(Boolean(), nullable=False, default=False)
    deleted_by_me = Column(Boolean(), nullable=False, default=False)
    url = Column(UnicodeText(), nullable=False)
    updating = Column(Boolean(), nullable=False, default=False)
    pause_update = Column(Boolean(), nullable=False, default=False)
    updating_interval = Column(Integer, nullable=False, default=60)
    rating = Column(Integer, nullable=False, default=0)
    sex = Column(Integer, nullable=False, default=5)
    photo = Column(UnicodeText(), nullable=False, default='')
    mobile_phone = Column(UnicodeText(), nullable=True)
    filter_by_albums = Column(UnicodeText(), nullable=True)

    albums = relationship('Album', back_populates='owner')
    photos = relationship('Photo', back_populates='owner')
    photos_of = relationship('Photo', secondary=photos_people, back_populates='peoples')

    def to_json(self):
        return obj_to_json(self)

    def __repr__(self):
        return 'User({} {})'.format(self.first_name, self.last_name)

    # def __eq__(self, other):
    #     return self.id == other.id
