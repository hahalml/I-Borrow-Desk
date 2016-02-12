import axios from 'axios';
import { store }  from '../index';

export const UPDATE_COMPANY_SEARCH = 'UPDATE_COMPANY_SEARCH';
export const RESET_COMPANY_SEARCH = 'RESET_COMPANY_SEARCH';
export const FETCH_STOCK = 'FETCH_STOCK';
export const FETCH_TRENDING = 'FETCH_TRENDING';
export const FETCH_WATCHLIST = 'FETCH_WATCHLIST';
export const ADD_WATCHLIST = 'ADD_WATCHLIST';
export const REMOVE_WATCHLIST = 'REMOVE_WATCHLIST';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGOUT_ACTION = 'LOGOUT_ACTION';
export const REGISTER_SUCCESS = 'REGISTER_SUCCESS';
export const REGISTER_FAILURE = 'REGISTER_FAILURE';
export const CHANGE_EMAIL_SUCCESS = 'CHANGE_EMAIL_SUCCESS';
export const CHANGE_PASSWORD_SUCCESS = 'CHANGE_PASSWORD_SUCCESS';
export const SHOW_LOGIN = 'SHOW_LOGIN';
export const HIDE_LOGIN = 'HIDE_LOGIN';
export const SHOW_PREFERENCES = 'SHOW_PREFERENCES';
export const HIDE_PREFERENCES = 'HIDE_PREFERENCES';
export const FETCH_PROFILE = 'FETCH_PROFILE';
export const CLEAR_MESSAGE = 'CLEAR_MESSAGE';
export const UPDATE_FILTER = 'UPDATE_FILTER';
export const UPDATE_MOST_EXPENSIVE = 'UPDATE_MOST_EXPENSIVE';

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

export const fetchTrending = () => {
  return dispatch => {
    return axios.get('/api/trending')
      .then(response => dispatch({type: FETCH_TRENDING, payload: response}))
      .catch(err => console.log(err));
  };
};

const makeAuthRequest = () => {
  const token = sessionStorage.token;
  return axios.create({
    headers: {'Authorization': `JWT ${token}`}
  });
};

export const fetchWatchlist = () => {
  return (dispatch, getState) => {
    return makeAuthRequest().get('/api/watchlist')
      .then(response => {
        dispatch({type: FETCH_WATCHLIST, payload: response});
      }).catch(err => {
        dispatch({type: SHOW_LOGIN, payload: err});
      });
  };
};

export const addWatchlist = symbol => {
  return (dispatch, getState) => {
    return makeAuthRequest().post('/api/watchlist', { symbol })
      .then(response => {
        dispatch({type: ADD_WATCHLIST, payload: symbol });
        dispatch({type: FETCH_WATCHLIST, payload: response });
      })
      .catch(err => dispatch({type: SHOW_LOGIN, payload: err}));
  };
};

export const removeWatchlist = symbol => {
  return (dispatch, getState) => {
    return makeAuthRequest().delete(`/api/watchlist?symbol=${symbol}`)
      .then(response => {
        dispatch({type: REMOVE_WATCHLIST, payload: symbol});
        dispatch({type: FETCH_WATCHLIST, payload: response});
      })
      .catch(err => dispatch({type: SHOW_LOGIN, payload: err}));
  };
};

export const showLoginAction = () => { return {'type': SHOW_LOGIN };};
export const hideLoginAction = () => { return {'type': HIDE_LOGIN };};

export const showPreferencesAction = () => { return {'type': SHOW_PREFERENCES };};
export const hidePreferencesAction = () => { return {'type': HIDE_PREFERENCES };};

export const submitLogin = (values, dispatch) => {
  return new Promise((resolve, reject) => {
    axios.post('/api/auth', values)
      .then(response => {
        dispatch({type: LOGIN_SUCCESS, payload: response.data.token });
        dispatch(fetchProfile());
        dispatch(fetchWatchlist());
        resolve();
      })
      .catch(error => {
        console.log('error in submitLogin', error);
        reject({username: 'Incorrect username or password',
          password: 'Incorrect username or password'});
      });
  });
};

export const fetchProfile = () => {
  return (dispatch, getState) => {
    return makeAuthRequest().get('/api/user')
      .then(response => {
        dispatch({type: FETCH_PROFILE, payload: response.data});
      }).catch(error => {
        console.log('error in fetch profile');
        dispatch({type: SHOW_LOGIN, payload: error});
      });
  };
}

export const toggleMorningEmail = () => {
  return (dispatch) => {
    return makeAuthRequest().post('/api/user/morning')
      .then(response => dispatch(fetchProfile()))
      .catch(err => console.log('error in toggle morning email'));
  }
}

export const submitNewEmail = (values, dispatch) => {
  return new Promise((resolve, reject) => {
    makeAuthRequest().post(`/api/user/email`, values)
      .then(response => {
        dispatch({type: CHANGE_EMAIL_SUCCESS });
        resolve();
      })
      .catch(error => {
        console.log('error in changeEmail', error);
        if (error.status == 401) reject({password: 'Password incorrect'});
        reject({...error.data.errors});
      });
  });
};

export const submitNewPassword = (values, dispatch) => {
  return new Promise((resolve, reject) => {
    makeAuthRequest().post(`/api/user/password`, values)
      .then(response => {
        dispatch({type: CHANGE_PASSWORD_SUCCESS });
        resolve();
      })
      .catch(error => {
        console.log('error in changePassword', error);
        if (error.status == 401) reject({password: 'Password incorrect'});
        reject({...error.data.errors});
      });
  });
};

export const logoutAction = () => {return {type: LOGOUT_ACTION};};

export const submitRegister = (values, dispatch) => {
  return new Promise((resolve, reject) => {
    axios.post('/api/register', values)
      .then(response => {
        dispatch({type: REGISTER_SUCCESS, payload: response});
        dispatch({type: SHOW_LOGIN});
        resolve();
      })
      .catch(error => {
        reject({...error.data.errors});
      });
  });
};

export const clearMessage = () => { return { 'type': CLEAR_MESSAGE };};

export const submitFilter = (values, dispatch) => {
  return new Promise((resolve, reject) => {
    axios.get('/api/filter', {params: values})
      .then(response => {
        dispatch({type: UPDATE_FILTER, payload: response});
        resolve();
      })
      .catch(error => {
        console.log('error in submitFilter', error);
        reject({...error.data.errors});
      });
  });
};

export const fetchMostExpensive = () => {
  return dispatch => {
    return axios.get('/api/filter/most_expensive')
      .then(response => dispatch({type: UPDATE_MOST_EXPENSIVE, payload: response}))
      .catch(err => console.log(err));
  };
};