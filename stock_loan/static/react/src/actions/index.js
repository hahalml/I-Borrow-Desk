import axios from 'axios';

export const UPDATE_COMPANY_SEARCH = 'UPDATE_COMPANY_SEARCH';
export const FETCH_STOCK = 'FETCH_STOCK';
export const FETCH_TRENDING = 'FETCH_TRENDING';
export const FETCH_WATCHLIST = 'FETCH_WATCHLIST';
export const ADD_WATCHLIST = 'ADD_WATCHLIST';
export const REMOVE_WATCHLIST = 'REMOVE_WATCHLIST';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGIN_FAILURE = 'LOGIN_FAILURE';
export const LOGOUT_ACTION = 'LOGOUT_ACTION';
export const AUTH_FAILURE = 'AUTH_FAILURE';

import { routeActions } from 'redux-simple-router';

export const searchCompany = name => {
  return dispatch => {
    return axios.get(`api/search/${name}`)
      .then(response => dispatch({type: UPDATE_COMPANY_SEARCH, payload: response}))
      .catch(err => console.log('error in searchCompany', err));
  };
};

export const fetchStock = ticker => {
  return dispatch => {
    return axios.get(`api/ticker/${ticker}`)
      .then(response => dispatch({type: FETCH_STOCK, payload: response}))
      .catch(err => console.log('error in fetchStock', err));
  };
};

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
        dispatch({type: AUTH_FAILURE, payload: err});
      });
  };
};

export const addWatchlist = symbol => {
  return dispatch => {
    return makeAuthRequest().post('/api/watchlist', { symbol })
      .then(response => dispatch({type: FETCH_WATCHLIST, payload: response}))
      .catch(err => dispatch({type: AUTH_FAILURE, payload: err}));
  };
};

export const removeWatchlist = symbol => {
  return dispatch => {
    return makeAuthRequest().delete(`/api/watchlist?symbol=${symbol}`)
      .then(response => dispatch({type: FETCH_WATCHLIST, payload: response}))
      .catch(err => dispatch({type: AUTH_FAILURE, payload: err}));
  };
};

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