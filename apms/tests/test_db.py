# -*- coding: utf-8 -*-
"""
Database test
"""
import datetime

from tornado_sqlalchemy import make_session_factory
from ..lib.db.database import Tag, User, Photo, Album, BASE

from sqlalchemy import Column, Integer, UnicodeText, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# pylint: disable=redefined-outer-name,missing-docstring

session_factory = make_session_factory('sqlite:////tmp/test.sqlite')
BASE.metadata.create_all(session_factory.engine)

def test_users_add():
    session = session_factory.make_session()
    user = user = User(
        first_name='Fn',
        last_name='Lm',
        url='url',
        date_added=datetime.datetime.now(),
        date_info_updated=datetime.datetime.now()
    )
    session.add(user)
    session.commit()
