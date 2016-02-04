import axios from 'axios';

export const UPDATE_COMPANY_SEARCH = 'UPDATE_COMPANY_SEARCH';
export const RESET_COMPANY_SEARCH = 'RESET_COMPANY_SEARCH';
export const FETCH_STOCK = 'FETCH_STOCK';
export const REAL_TIME = 'REAL_TIME';
export const DAILY = 'DAILY';
export const FETCH_TRENDING = 'FETCH_TRENDING';
export const FETCH_WATCHLIST = 'FETCH_WATCHLIST';
export const ADD_WATCHLIST = 'ADD_WATCHLIST';
export const REMOVE_WATCHLIST = 'REMOVE_WATCHLIST';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGIN_FAILURE = 'LOGIN_FAILURE';
export const LOGOUT_ACTION = 'LOGOUT_ACTION';
export const SHOW_LOGIN = 'SHOW_LOGIN';

import { routeActions } from 'redux-simple-router';

export const searchCompany = name => {
  return dispatch => {
    return axios.get(`api/search/${name}`)
      .then(response => dispatch({type: UPDATE_COMPANY_SEARCH, payload: response}))
      .catch(err => console.log('error in searchCompany', err));
  };
};

export const resetCompanySearch = () => { return {'type': RESET_COMPANY_SEARCH };};

export const fetchStock = ticker => {
  return dispatch => {
    return axios.get(`api/ticker/${ticker}`)
      .then(response => dispatch({type: FETCH_STOCK, payload: response}))
      .catch(err => console.log('error in fetchStock', err));
  };
};

export const viewRealTime = () => { return {'type': REAL_TIME };};
export const viewDaily = () => { return {'type': DAILY };};

export const fetchTrending = () => {
  return dispatch => {
    return axios.get('/api/trending')
      .then(response => dispatch({type: FETCH_TRENDING, payload: response}))
      .catch(err => console.log(err));
  };
};

export const makeAuthRequest = () => {
  return axios.create({
    headers: {'Authorization': `JWT ${localStorage.getItem('token')}`}
  });
};

export const fetchWatchlist = () => {
  return dispatch => {
    return makeAuthRequest().get('/api/watchlist')
      .then(response => {
        dispatch({type: FETCH_WATCHLIST, payload: response});
      }).catch(err => {
        dispatch({type: SHOW_LOGIN, payload: err});
      });
  };
};

export const addWatchlist = symbol => {
  return dispatch => {
    return makeAuthRequest().post('/api/watchlist', { symbol })
      .then(response => dispatch({type: FETCH_WATCHLIST, payload: response}))
      .catch(err => dispatch({type: SHOW_LOGIN, payload: err}));
  };
};

export const removeWatchlist = symbol => {
  return dispatch => {
    return makeAuthRequest().delete(`/api/watchlist?symbol=${symbol}`)
      .then(response => dispatch({type: FETCH_WATCHLIST, payload: response}))
      .catch(err => dispatch({type: SHOW_LOGIN, payload: err}));
  };
};

export const showLoginAction = () => { return {'type': SHOW_LOGIN };};

export function submitLogin (props) {
  return dispatch => {
    axios.post('/api/auth', props)
      .then(response => {
        localStorage.setItem('token', response.data.access_token);
        dispatch({type: LOGIN_SUCCESS, payload: response});
        dispatch(fetchWatchlist());
        dispatch(routeActions.push('/watchlist'));
      })
      .catch(error => {
        console.log('error in submit login', error);
        dispatch({type: LOGIN_FAILURE, payload: error});
      });
  }
}

export function logoutAction() {
  localStorage.setItem('token', null);
  return {type: LOGOUT_ACTION}
}