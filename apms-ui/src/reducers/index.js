import { combineReducers } from 'redux';
import userReducer from './usersReducer';
import photosReducer from './photosReducer';

export default combineReducers({
    userReducer,
    photos: photosReducer
});
