"""Added 'pause_update' field

Revision ID: add6265f2306
Revises: 8abc70088073
Create Date: 2018-09-25 18:12:53.872002

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy import (
    Column,
    Integer,
    UnicodeText,
    DateTime,
    Boolean,
    ForeignKey,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# revision identifiers, used by Alembic.
revision = "add6265f2306"
down_revision = "8abc70088073"
branch_labels = None
depends_on = None

BASE = declarative_base()
Session = sessionmaker()

photos_tags = Table(
    "__photos_tags__",
    BASE.metadata,
    Column("photo_id", ForeignKey("photos.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

photos_people = Table(
    "__photos_people__",
    BASE.metadata,
    Column("photo_id", ForeignKey("photos.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

photos_albums = Table(
    "__photos_albums__",
    BASE.metadata,
    Column("photo_id", ForeignKey("photos.id"), primary_key=True),
    Column("album_id", ForeignKey("albums.id"), primary_key=True),
)


def to_unit_timestamp(date_time):
    if not date_time:
        return 0
    return int(mktime(date_time.timetuple()))


def obj_to_json(obj):
    data = obj.__dict__.copy()
    del data["_sa_instance_state"]
    for key, _ in data.items():
        if key.startswith("date"):
            data[key] = to_unit_timestamp(data[key])
    return data


class Settings(BASE):
    __tablename__ = "status_and_settings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    pause_update = Column(Boolean(), nullable=False, default=False)


class Tag(BASE):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    slug = Column(UnicodeText(), nullable=False, unique=True)
    title = Column(UnicodeText(), nullable=False, unique=True)

    photos = relationship("Photo", secondary=photos_tags, back_populates="tags")

    def to_json(self):
        return {"id": self.id, "slug": self.slug, "title": self.title}


class Album(BASE):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    origin_id = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(UnicodeText(), nullable=False)
    description = Column(UnicodeText(), nullable=False)
    rating = Column(Integer, nullable=False, default=0)

    owner = relationship("User", back_populates="albums")
    photos = relationship("Photo", secondary=photos_albums, back_populates="albums")

    def to_json(self):
        return obj_to_json(self)


class Photo(BASE):
    __tablename__ = "photos"
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="photos")

    peoples = relationship("User", secondary=photos_people, back_populates="photos_of")
    tags = relationship("Tag", secondary=photos_tags, back_populates="photos")
    albums = relationship("Album", secondary=photos_albums, back_populates="photos")

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
        data["local_url"] = "/files/photos/" + self.dir_name + "/" + self.file_name
        data["owner"] = self.owner.to_json() if self.owner else {}
        return data


class User(BASE):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    kind = Column(Integer, nullable=False, default=0)  # 0 - user, 1 - group
    first_name = Column(UnicodeText(), nullable=False, default="")
    last_name = Column(UnicodeText(), nullable=False, default="")
    domain = Column(UnicodeText(), nullable=True)
    nick_name = Column(UnicodeText(), nullable=True, default="")
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
    photo = Column(UnicodeText(), nullable=False, default="")
    mobile_phone = Column(UnicodeText(), nullable=True)
    filter_by_albums = Column(UnicodeText(), nullable=True)

    albums = relationship("Album", back_populates="owner")
    photos = relationship("Photo", back_populates="owner")
    photos_of = relationship("Photo", secondary=photos_people, back_populates="peoples")

    def to_json(self):
        return obj_to_json(self)

    def __repr__(self):
        return "User({} {})".format(self.first_name, self.last_name)


class OldUser(BASE):
    __tablename__ = "old_users"
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    kind = Column(Integer, nullable=False, default=0)  # 0 - user, 1 - group
    first_name = Column(UnicodeText(), nullable=False, default="")
    last_name = Column(UnicodeText(), nullable=False, default="")
    domain = Column(UnicodeText(), nullable=True)
    nick_name = Column(UnicodeText(), nullable=True, default="")
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
    updating_interval = Column(Integer, nullable=False, default=60)
    rating = Column(Integer, nullable=False, default=0)
    sex = Column(Integer, nullable=False, default=5)
    photo = Column(UnicodeText(), nullable=False, default="")
    mobile_phone = Column(UnicodeText(), nullable=True)
    filter_by_albums = Column(UnicodeText(), nullable=True)

    # albums = relationship('Album', back_populates='owner')
    # photos = relationship('Photo', back_populates='owner')
    # photos_of = relationship('Photo', secondary=photos_people, back_populates='peoples')

    def to_json(self):
        return obj_to_json(self)

    def __repr__(self):
        return "User({} {})".format(self.first_name, self.last_name)


def upgrade():
    op.rename_table("users", "old_users")

    bind = op.get_bind()
    session = Session(bind=bind)

    # create the tables
    User.__table__.create(bind)

    for old_user in session.query(OldUser).all():
        user = User(
            id=old_user.id,
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
            updating_interval=old_user.updating_interval,
            rating=old_user.rating,
            sex=old_user.sex,
            photo=old_user.photo,
            mobile_phone=old_user.mobile_phone,
            filter_by_albums=old_user.filter_by_albums,
        )
        session.add(user)
    session.commit()
    op.drop_table("old_users")


def downgrade():
    pass
