export const makeSearchParams = (setParams, search = null) => {
    let params = new URLSearchParams(search);
    for (const [key, value] of Object.entries(setParams)) {
        params.set(key, value);
    }
    return params.toString();
};
