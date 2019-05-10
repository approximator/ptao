import { SHIFT_DOWN, SHIFT_UP } from './types';

export const shiftDown = () => dispatch => {
    dispatch({
        type: SHIFT_DOWN,
        payload: {}
    });
};

export const shiftUp = () => dispatch => {
    dispatch({
        type: SHIFT_UP,
        payload: {}
    });
};
