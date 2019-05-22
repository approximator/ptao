import {
    FETCH_PHOTOS,
    CURRENT_IMAGE_CHANGE,
    LIGHTBOX_CLOSE,
    LIGHTBOX_PREV,
    LIGHTBOX_NEXT,
    IMAGE_CLICK,
    LIGHTBOX_OPEN,
    SHIFT_DOWN,
    SHIFT_UP,
    DELETE_PHOTOS
} from '../actions/types';

const initialState = {
    result: 'ok',
    reason: 'Init',
    message: 'Initialization',
    keyboard: {},
    photos: [],
    totalPhotosCount: 0,
    totalPages: 0,
    currentPage: 1,

    users: [],
    currentImage: 0,
    lightboxIsOpen: false,
    lastClickedImage: undefined,
    photosPerPage: 200,
    sidebarVisible: false,
    selectionModeEnabled: false,
    shiftPressed: false,

    tagPeopleModalOpened: false,
    selectedImages: [],

    sortBy: 'date-downloaded'
};

export default function(state = initialState, action) {
    switch (action.type) {
        case FETCH_PHOTOS:
            console.log('Photos reducer. action.payload = ', action.payload);
            // TODO: if result === 'ok'
            return {
                ...state,
                photos: action.payload.photos,
                totalPhotosCount: action.payload.totalPhotosCount,
                totalPages: action.payload.totalPages,
                currentPage: action.payload.page
            };

        case CURRENT_IMAGE_CHANGE:
            return {
                ...state,
                currentImage: action.payload.currentImage
            };

        case LIGHTBOX_OPEN:
            return {
                ...state,
                currentImage: action.payload.index,
                lightboxIsOpen: true
            };

        case LIGHTBOX_CLOSE:
            return {
                ...state,
                lightboxIsOpen: false
            };

        case LIGHTBOX_PREV:
            const nextImageIndex = state.photos
                ? (state.currentImage + state.photos.length - 1) % state.photos.length
                : 0;
            return {
                ...state,
                currentImage: nextImageIndex
            };

        case LIGHTBOX_NEXT:
            const prevImageIndex = state.photos ? (state.currentImage + 1) % state.photos.length : 0;
            return {
                ...state,
                currentImage: prevImageIndex
            };

        case SHIFT_DOWN:
            return {
                ...state,
                shiftPressed: true
            };

        case SHIFT_UP:
            return {
                ...state,
                shiftPressed: false
            };

        case IMAGE_CLICK:
            let { lastClickedImage, selectionModeEnabled, shiftPressed } = state;
            let photos = state.photos.slice();
            let lightboxIsOpen = false;
            if (shiftPressed) {
                selectionModeEnabled = true;
            }
            console.log('selectionModeEnabled: ', selectionModeEnabled);
            console.log('shiftPressed: ', shiftPressed);
            if (selectionModeEnabled) {
                let photos = state.photos;
                if (shiftPressed && typeof lastClickedImage !== 'undefined') {
                    const startIndex = Math.min(lastClickedImage, action.payload.index);
                    const lastIndex = Math.max(lastClickedImage, action.payload.index);
                    let idx;
                    for (idx = startIndex; idx <= lastIndex; idx++) {
                        photos[idx].selected = true;
                    }
                } else {
                    console.log('Invert selection of ', action.payload.index);
                    photos[action.payload.index].selected = !photos[action.payload.index].selected;
                }
                lastClickedImage = action.payload.index;
                selectionModeEnabled = photos.filter(photo => photo.selected === true).length > 0;
                if (!selectionModeEnabled) {
                    lastClickedImage = undefined;
                }
            } else {
                lightboxIsOpen = true;
            }

            return {
                ...state,
                photos: photos,
                currentImage: action.payload.index,
                lightboxIsOpen: lightboxIsOpen,
                lastClickedImage: lastClickedImage,
                selectionModeEnabled: selectionModeEnabled
            };

        case DELETE_PHOTOS:
            return {
                ...state,
                photos: state.photos.filter(photo => !action.payload.deletedPphotos.includes(photo)),
                selectionModeEnabled: false,
                lastClickedImage: undefined
            };

        default:
            return state;
    }
}
