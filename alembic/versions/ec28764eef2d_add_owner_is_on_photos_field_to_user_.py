"""Add "owner_is_on_photos" field to User table

Revision ID: ec28764eef2d
Revises: add6265f2306
Create Date: 2018-10-05 17:41:22.627838

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy import Column, Integer, UnicodeText, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

BASE = declarative_base()
Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = 'ec28764eef2d'
down_revision = 'add6265f2306'
branch_labels = None
depends_on = None


class OldUser(BASE):
    __tablename__ = 'old_users'
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
    owner_is_on_photos = Column(Boolean(), nullable=False, default=False)


def upgrade():
    op.rename_table('users', 'old_users')

    bind = op.get_bind()
    session = Session(bind=bind)

    # create the tables
    User.__table__.create(bind)

    for old_user in session.query(OldUser).all():
        user = User(
            id=old_user.id,
            kind=old_user.kind,
            first_name=old_user.first_name,
            last_name=old_user.last_name,
            domain=old_user.domain,
            nick_name=old_user.nick_name,
            site=old_user.site,
            status_str=old_user.status_str,
            about=old_user.about,
            date_birthday=old_user.date_birthday,
            city=old_user.city,
            date_added=old_user.date_added,
            date_info_updated=old_user.date_info_updated,
            date_photos_updated=old_user.date_photos_updated,
            date_info_updated_successfully=old_user.date_info_updated_successfully,
            date_photos_updated_successfully=old_user.date_photos_updated_successfully,
            deleted=old_user.deleted,
            deleted_by_me=old_user.deleted_by_me,
            url=old_user.url,
            updating=old_user.updating,
            pause_update=old_user.pause_update,
            updating_interval=old_user.updating_interval,
            rating=old_user.rating,
            sex=old_user.sex,
            photo=old_user.photo,
            mobile_phone=old_user.mobile_phone,
            filter_by_albums=old_user.filter_by_albums)
        session.add(user)
    session.commit()
    op.drop_table('old_users')


def downgrade():
    pass
