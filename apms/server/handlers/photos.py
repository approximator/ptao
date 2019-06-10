import os
import json
import shutil
import logging

from sqlalchemy import not_
from sqlalchemy.orm import joinedload
from tornado.web import RequestHandler
from tornado_sqlalchemy import SessionMixin

from apms.lib.config import config
from apms.lib.db.database import Photo, User

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class PhotosHandler(RequestHandler, SessionMixin):
    """
    Handler for API methods of photos functions
    """

    def get(self):  # pylint: disable=too-many-locals
        """Get photos
        """
        page = int(self.get_query_argument('page', 1))
        limit = int(self.get_query_argument('elements_per_page', 200))
        offset = (page - 1) * limit
        owner_id = self.get_query_argument('owner_id', None)
        photos_of = self.get_query_argument('photos_of', None)
        photos_by = self.get_query_argument('photos_by', None)
        sort_by = self.get_query_argument('sort_by', 'date-downloaded')
        missing = self.get_query_argument('missing', None)
        to_delete = self.get_query_argument('to_delete', None)
        # foreign = self.get_query_argument('foreign', None)
        small = self.get_query_argument('small', None)
        photo_text = self.get_query_argument('photo_text', None)

        with self.make_session() as session:
            if to_delete is not None:
                count, result = PhotosHandler.get_photos_to_delete(session)
            elif missing is not None:
                count, result = PhotosHandler.get_missing_photos(session)
            else:
                query = session.query(Photo).options(joinedload(Photo.owner)).filter(not_(Photo.deleted_by_me))
                if owner_id:
                    query = query.filter_by(owner_id=owner_id)
                if small:
                    query = query.filter(Photo.width < 450)
                if photos_of is not None:
                    query = query.filter(Photo.people.any(User.id == photos_of))
                if photos_by is not None:
                    query = query.filter(Photo.authors.any(User.id == photos_by))
                if photo_text is not None:
                    query = query.filter(Photo.text.ilike(f'%{photo_text}%'))

                if sort_by == 'date-downloaded':
                    query = query.order_by(Photo.date_downloaded.desc())
                elif sort_by == 'date-taken':
                    query = query.order_by(Photo.date_added.desc())
                elif sort_by == 'rating':
                    query = query.order_by(Photo.rating.desc())

                count = query.count()
                result = query.offset(offset).limit(limit).all()

            photos = {'count': count, 'page': page, 'photos': list(map(lambda photo: photo.to_json(), result))}
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(photos))

    @staticmethod
    def get_missing_photos(session):
        query = session.query(Photo).options(joinedload(Photo.owner)).filter_by(deleted_by_me=False)
        result = list(
            filter(lambda photo: not os.path.exists(os.path.join(config.photos_dir, photo.dir_name, photo.file_name)),
                   query.order_by(Photo.date_added.desc()).all()))
        return len(result), result[0:200]

    @staticmethod
    def get_photos_to_delete(session):
        query = session.query(Photo).options(joinedload(Photo.owner)).filter_by(deleted_by_me=True)
        result = list(
            filter(lambda photo: os.path.exists(os.path.join(config.photos_dir, photo.dir_name, photo.file_name)),
                   query.order_by(Photo.date_downloaded.desc()).all()))
        return len(result), result

    def delete(self):
        try:
            photos_to_delete = json.loads(self.request.body.decode())['photos']
        except Exception as ex:  # pylint: disable=broad-except
            log.info(ex)
            self.set_status(400)
            self.write(json.dumps({'result': 'Error', 'cause': 'Wrong request', 'description': str(ex)}))
            return

        log.info('Going to remove {}'.format(photos_to_delete))
        with self.make_session() as session:
            query = session.query(Photo).filter(Photo.id.in_(photos_to_delete))
            count = query.count()
            if not count:
                self.set_status(404)
                self.write(json.dumps({'result': 'Error', 'cause': 'Not Found'}))
                return
            for photo in query.all():
                if not os.path.isdir(config.trash_dir):
                    os.makedirs(config.trash_dir)

                photo.deleted_by_me = True
                fname = os.path.join(config.photos_dir, photo.dir_name, photo.file_name)
                new_fname = os.path.join(config.trash_dir, photo.file_name)
                log.info('Moving {} -> {}'.format(fname, new_fname))
                try:
                    shutil.move(fname, new_fname)
                except OSError:
                    log.exception('Cannot move {} -> {}'.format(fname, new_fname))
                log.info('{} marked as deleted by me'.format(photo.id))
            session.commit()

            self.write(json.dumps({'result': 'Ok', 'deleted': photos_to_delete}))
