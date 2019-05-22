import {
    FETCH_USERS,
    PAUSE_UPDATE,
    OPEN_USER_INFO,
    CLOSE_USER_INFO,
    UPDATE_USER_INFO_DEFAULT_PERSONS,
    OPEN_TAG_PEOPLE_DIALOG,
    CLOSE_TAG_PEOPLE_DIALOG,
    SAVE_PEOPLE_TAGS
} from '../actions/types';

const initialState = {
    users: [],
    peopleDropdownList: [],
    currentUser: undefined,
    userInfoOpen: false,
    success: 'unknown',

    tagUsersDialogOpen: false
};

function createOptions(user) {
    return {
        key: user.id,
        value: user.id,
        text: `${user.first_name} ${user.last_name} `
    };
}

export default function(state = initialState, action) {
    switch (action.type) {
        case FETCH_USERS:
            console.log('User reducer. action.payload = ', action.payload);
            return {
                ...state,
                users: action.payload.users,
                peopleDropdownList: action.payload.users.map(createOptions)
            };

        case OPEN_TAG_PEOPLE_DIALOG:
            return {
                ...state,
                photos: action.payload.photos,
                tagUsersDialogOpen: true
            };

        case CLOSE_TAG_PEOPLE_DIALOG:
            return {
                ...state,
                tagUsersDialogOpen: false
            };

        case OPEN_USER_INFO:
            return {
                ...state,
                currentUser: action.payload.user_id,
                userInfoOpen: true
            };

        case CLOSE_USER_INFO:
            return {
                ...state,
                userInfoOpen: false
            };

        case PAUSE_UPDATE:
            console.log('User reducer. action.payload = ', action.payload);
            return {
                ...state,
                users: state.users.map(user => {
                    if (user.id === action.payload.user_id) {
                        return { ...user, pause_update: action.payload.paused };
                    } else {
                        return user;
                    }
                })
            };

        case SAVE_PEOPLE_TAGS:
            return {
                ...state,
                success: action.payload.result
            };

        case UPDATE_USER_INFO_DEFAULT_PERSONS:
            return {
                ...state
            };

        default:
            return state;
    }
}
