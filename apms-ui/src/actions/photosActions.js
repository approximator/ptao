import {
    FETCH_PHOTOS,
    CURRENT_IMAGE_CHANGE,
    LIGHTBOX_OPEN,
    LIGHTBOX_CLOSE,
    LIGHTBOX_PREV,
    LIGHTBOX_NEXT,
    IMAGE_CLICK,
    DELETE_PHOTOS,
    DESELECT_ALL
} from '../actions/types';

export const deselectAll = () => dispatch => {
    dispatch({
        type: DESELECT_ALL,
        payload: {}
    });
};

export const lightboxOpen = imageIndex => dispatch => {
    dispatch({
        type: LIGHTBOX_OPEN,
        payload: {
            index: imageIndex
        }
    });
};

export const lightboxClose = () => dispatch => {
    dispatch({
        type: LIGHTBOX_CLOSE,
        payload: {}
    });
};

export const imageClick = (event, obj) => dispatch => {
    dispatch({
        type: IMAGE_CLICK,
        payload: {
            index: obj.index
        }
    });
};

export const lightboxPrev = () => dispatch => {
    dispatch({
        type: LIGHTBOX_PREV,
        payload: {}
    });
};

export const lightboxNext = () => dispatch => {
    dispatch({
        type: LIGHTBOX_NEXT,
        payload: {}
    });
};

export const currentImageChange = index => dispatch => {
    dispatch({
        type: CURRENT_IMAGE_CHANGE,
        payload: {
            currentImage: index
        }
    });
};

const createImgObj = (is_missing, photo) => {
    return {
        key: photo.id,
        id: photo.id,
        origin_id: photo.origin_id,
        owner_id: photo.owner_id,
        onwer_name: photo.owner.first_name + ' ' + photo.owner.last_name,
        src: is_missing ? photo.url : photo.local_url,
        thumbnail: is_missing ? photo.url : photo.local_url,
        text: photo.text,
        caption: photo.text,
        width: photo.width,
        height: photo.height,
        people_tags: photo.people.map(user => {
            return { id: user.id, first_name: user.first_name, last_name: user.last_name };
        }),
        authors: photo.authors.map(user => {
            return { id: user.id, first_name: user.first_name, last_name: user.last_name };
        })
    };
};

export const fetchPhotos = searchParams => dispatch => {
    let params = new URLSearchParams(searchParams);
    const page = params.has('page') ? parseInt(params.get('page')) : 1;
    const photosPerPage = params.has('elements_per_page') ? parseInt(params.get('elements_per_page')) : 200;
    params.set('elements_per_page', photosPerPage);
    params.set('page', page);
    const url = '/api/photos?' + params.toString();

    fetch(url)
        .then(res => res.json())
        .then(data =>
            dispatch({
                type: FETCH_PHOTOS,
                payload: {
                    result: 'ok',
                    reason: 'Success',
                    message: 'Success',
                    photos: data.photos.map(photo => createImgObj(params.has('missing'), photo)),
                    totalPhotosCount: data['count'],
                    totalPages: Math.ceil(Number(data['count']) / photosPerPage),
                    page: parseInt(data['page'])
                }
            })
        );
};

export const deletePhotos = photosToDelete => dispatch => {
    const data = {
        photos: photosToDelete.map(img => img.id)
    };

    const options = {
        method: 'delete',
        headers: { 'Content-type': 'application/json; charset=UTF-8' },
        body: JSON.stringify(data)
    };

    fetch('/api/photos', options)
        .then(res => res.json())
        .then(data =>
            dispatch({
                type: DELETE_PHOTOS,
                payload: {
                    result: 'ok',
                    reason: 'Success',
                    message: 'Success',
                    deletedPphotos: photosToDelete
                }
            })
        )
        .catch(err => console.error(err));
};
