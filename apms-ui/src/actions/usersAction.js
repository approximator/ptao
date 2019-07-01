import {
    FETCH_USERS,
    PAUSE_UPDATE,
    OPEN_USER_INFO,
    CLOSE_USER_INFO,
    FETCH_USER_INFO,
    UPDATE_USER_INFO_DEFAULT_PERSONS,
    OPEN_TAG_PEOPLE_DIALOG,
    CLOSE_TAG_PEOPLE_DIALOG,
    SAVE_PEOPLE_TAGS
} from '../actions/types';

export const tagPeopleDialogOpen = photos => dispatch => {
    dispatch({
        type: OPEN_TAG_PEOPLE_DIALOG,
        payload: {
            photos: photos
        }
    });
};

export const tagPeopleDialogClose = () => dispatch => {
    dispatch({
        type: CLOSE_TAG_PEOPLE_DIALOG,
        payload: {}
    });
};

export const fetchUserInfo = userId => dispatch => {
    fetch('/api/users/' + userId + '/update')
        .then(res => res.json())
        .then(data => {
            console.log(data);
            dispatch({
                type: FETCH_USER_INFO,
                payload: {
                    info: data,
                    gotInfo: true,
                    infoIsLoading: false
                }
            });
        })
        .catch(err => {
            console.error(err);
            dispatch({
                type: FETCH_USER_INFO,
                payload: {
                    info: {},
                    gotInfo: false,
                    infoIsLoading: false
                }
            });
        });
};

// addUser() {
//     const options = {
//         method: 'put',
//         headers: { 'Content-type': 'application/json; charset=UTF-8' }
//     };
//     fetch('/api/users/' + this.state.userId + '/update', options)
//         .then(res => res.json())
//         .then(data => {
//             console.log(data);
//         })
//         .catch(err => {
//             console.error(err);
//             this.setState({ infoIsLoading: false });
//         });
// }

export const fetchUsers = () => dispatch => {
    fetch('/api/users')
        .then(res => res.json())
        .then(users =>
            dispatch({
                type: FETCH_USERS,
                payload: users
            })
        );
};

export const userInfoOpen = user_id => dispatch => {
    dispatch({
        type: OPEN_USER_INFO,
        payload: {
            user_id: user_id
        }
    });
};

export const userInfoClose = () => dispatch => {
    dispatch({
        type: CLOSE_USER_INFO,
        payload: {}
    });
};

export const pauseUpdate = (user_id, pause) => dispatch => {
    dispatch({
        type: PAUSE_UPDATE,
        payload: {
            result: 'error',
            reason: 'Not implemented yet',
            message: 'Not implemented yet',
            paused: pause,
            user_id: user_id
        }
    });
};

export const saveUserTags = (photos, people, authors, overwritePeopleTags, overwriteAuthorsTags) => dispatch => {
    const data = {
        photos: photos.map(ph => ph.id),
        people: people,
        authors: authors,
        overwrite_people_tags: overwritePeopleTags,
        overwrite_authors_tags: overwriteAuthorsTags
    };

    const options = {
        method: 'put',
        headers: { 'Content-type': 'application/json; charset=UTF-8' },
        body: JSON.stringify(data)
    };

    fetch('/api/photos/tagPeople', options)
        .then(response => response.json())
        .then(body => {
            console.log(body);
            dispatch({
                type: SAVE_PEOPLE_TAGS,
                payload: {
                    ...body
                }
            });
        })
        .catch(err => {
            console.error(err);
            dispatch({
                type: SAVE_PEOPLE_TAGS,
                payload: {
                    err
                }
            });
        });
};

export const updateUserInfoDefaultPersons = (user_id, default_author, default_person_to_tag) => dispatch => {
    dispatch({
        type: UPDATE_USER_INFO_DEFAULT_PERSONS,
        payload: {
            result: 'error',
            reason: 'Not implemented yet',
            message: 'Not implemented yet',
            user_id: user_id
        }
    });
};
