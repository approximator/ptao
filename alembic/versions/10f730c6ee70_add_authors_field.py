"""Add authors field

Revision ID: 10f730c6ee70
Revises: ec28764eef2d
Create Date: 2018-10-09 17:10:52.911527

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy import Column, Integer, UnicodeText, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

BASE = declarative_base()
Session = sessionmaker()

# revision identifiers, used by Alembic.
revision = '10f730c6ee70'
down_revision = 'ec28764eef2d'
branch_labels = None
depends_on = None

photos_tags = Table('__photos_tags__', BASE.metadata, Column('photo_id', ForeignKey('photos.id'), primary_key=True),
                    Column('tag_id', ForeignKey('tags.id'), primary_key=True))

photos_people = Table('__photos_people__', BASE.metadata, Column('photo_id', ForeignKey('photos.id'), primary_key=True),
                      Column('user_id', ForeignKey('users.id'), primary_key=True))

photos_authors = Table('__photos_authors__', BASE.metadata, Column(
    'photo_id', ForeignKey('photos.id'), primary_key=True), Column('user_id', ForeignKey('users.id'), primary_key=True))

# photos_albums = Table('__photos_albums__', BASE.metadata, Column('photo_id', ForeignKey('photos.id'), primary_key=True),
#                       Column('album_id', ForeignKey('albums.id'), primary_key=True))


class OldPhoto(BASE):
    __tablename__ = 'old_photos'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)

    owner_id = Column(Integer, ForeignKey('users.id'))

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
    owner_is_on_photos = Column(Boolean(), nullable=False, default=False)


class Photo(BASE):
    __tablename__ = 'photos'
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    people = relationship('User', secondary=photos_people, back_populates='photos_of')
    authors = relationship('User', secondary=photos_authors, back_populates='photos_by')

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="photos")

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
    default_person_to_tag = Column(Integer, ForeignKey('users.id'), nullable=True)
    default_author = Column(Integer, ForeignKey('users.id'), nullable=True)

    # albums = relationship('Album', back_populates='owner')
    photos = relationship('Photo', back_populates='owner')
    photos_of = relationship('Photo', secondary=photos_people, back_populates='people')
    photos_by = relationship('Photo', secondary=photos_authors, back_populates='authors')


def upgrade():
    op.rename_table('users', 'old_users')
    op.rename_table('photos', 'old_photos')

    bind = op.get_bind()
    session = Session(bind=bind)

    # create the tables
    User.__table__.create(bind)
    Photo.__table__.create(bind)
    photos_authors.create(bind)

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

        if old_user.owner_is_on_photos:
            user.default_person_to_tag = old_user.id
        # default_author = Column(Integer, ForeignKey('users.id'), nullable=True)
        session.add(user)
    for old_photo in session.query(OldPhoto).all():
        photo = Photo(
            origin_id=old_photo.origin_id,
            owner_id=old_photo.owner_id,
            rating=old_photo.rating,
            url=old_photo.url,
            dir_name=old_photo.dir_name,
            file_name=old_photo.file_name,
            new=old_photo.new,
            date_downloaded=old_photo.date_downloaded,
            date_info_updated=old_photo.date_info_updated,
            date_info_updated_successfully=old_photo.date_info_updated_successfully,
            deleted=old_photo.deleted,
            deleted_by_me=old_photo.deleted_by_me,
            updating_interval=old_photo.updating_interval,
            date_added=old_photo.date_added,
            width=old_photo.width,
            height=old_photo.height,
            text=old_photo.text)
        session.add(photo)

    session.commit()
    op.drop_table('old_users')
    op.drop_table('old_photos')


def downgrade():
    pass
