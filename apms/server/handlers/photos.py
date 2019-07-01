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

from apms.server.api_schemas import PeopleTagRequest, ApiResult

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class PhotosHandler(RequestHandler, SessionMixin):
    """
    Handler for API methods of photos functions
    """

    def get(self):  # pylint: disable=too-many-locals
        """Get photos
        ---
        summary: Get photos
        tags:
          - "Photos"
        parameters:
        - in: query
          name: page
          schema:
            type: integer
          description: Return photos from specified page
        - in: query
          name: elements_per_page
          schema:
            type: integer
          description: Number of photos on a page
        - in: query
          name: owner_id
          schema:
            type: integer
          description: Return photos of specified owner
        - in: query
          name: photos_of
          schema:
            type: integer
          description: Return photos of specified person
        - in: query
          name: photos_by
          schema:
            type: integer
          description: Return photos made by a specified author
        - in: query
          name: sort_by
          schema:
            type: string
            enum: ['date-downloaded', 'date-taken', 'rating']
          description: Sorting order
        - in: query
          name: photo_text
          schema:
            type: string
          description: Search specified pattern in photo text
        responses:
          200:
            description: Information about head unit
            schema: GetPhotosResponseSchema
        """
        page = int(self.get_query_argument('page', 1))
        limit = int(self.get_query_argument('elements_per_page', 100))
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
        """Delete photos
        ---
        summary: Delete photos
        tags:
          - "Photos"
        parameters:
          - name: data
            in: body
            description: List of photos to delete
            required: true
            schema: DeletePhotosRequest

        responses:
          200:
            schema: ApiResult
          400:
            schema: ApiResult
        """
        try:
            photos_to_delete = json.loads(self.request.body.decode())['photos']
        except Exception as ex:  # pylint: disable=broad-except
            log.info(ex)
            resp = ApiResult('error', str(ex))
            self.set_status(400)
            self.write(ApiResult.Schema().dumps(resp))
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

            resp = ApiResult('success', f'deleted: {photos_to_delete}')
            self.write(ApiResult.Schema().dumps(resp))


class PeopleTagHandler(RequestHandler, SessionMixin):

    async def put(self):
        """Tag people
        ---
        summary: Tag people on photo
        tags:
          - "Photos"
        parameters:
          - name: data
            in: body
            description: List of photos to tad along with list of people to add to each photo
            required: true
            schema: PeopleTagRequest

        responses:
          200:
            schema: ApiResult
          400:
            schema: ApiResult
        """
        try:
            data = self.request.body.decode()
            log.info(data)
            params = PeopleTagRequest.Schema().loads(data)

            with self.make_session() as session:
                people = session.query(User).filter(User.id.in_(params.people)).all()
                authors = session.query(User).filter(User.id.in_(params.authors)).all()
                for photo in session.query(Photo).filter(Photo.id.in_(params.photos)).all():
                    photo.people = people if params.overwrite_people_tags else list(set(people + photo.people))
                    photo.authors = authors if params.overwrite_authors_tags else list(set(authors + photo.authors))
                session.commit()

        except Exception as ex:  # pylint: disable=broad-except
            log.info(ex)
            resp = ApiResult('error', str(ex))
            self.set_status(400)
            self.write(ApiResult.Schema().dumps(resp))
            return

        resp = ApiResult('success', 'Tags have been added')
        self.write(ApiResult.Schema().dumps(resp))
