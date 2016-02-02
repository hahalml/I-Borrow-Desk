import axios from 'axios';

export const UPDATE_COMPANY_SEARCH = 'UPDATE_COMPANY_SEARCH';
export const FETCH_STOCK = 'FETCH_STOCK';
export const FETCH_TRENDING = 'FETCH_TRENDING';
export const FETCH_WATCHLIST = 'FETCH_WATCHLIST';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGIN_FAILURE = 'LOGIN_FAILURE';
export const LOGOUT_ACTION = 'LOGOUT_ACTION';

export const searchCompany = name => {
  const url = `api/search/${name}`;
  const response = axios.get(url);
  return {
    type: UPDATE_COMPANY_SEARCH,
    payload: response
  };
};

export const fetchStock = ticker => {
  const response = axios.get(`api/ticker/${ticker}`);
  return {
    type: FETCH_STOCK,
    payload: response
  }
};

export const fetchTrending = () => {
  const response = axios.get('/api/trending');
  return {
    type: FETCH_TRENDING,
    payload: response
  }
};

export const makeAuthRequest = () => {
  console.log(localStorage.getItem('token'));
  return axios.create({
    headers: {'Authorization': `JWT ${localStorage.getItem('token')}`}
  });
};

export const fetchWatchlist = () => {
  const response = makeAuthRequest().get('/api/watchlist');
  return {
    type: FETCH_WATCHLIST,
    payload: response
  }
};

export function submitLogin (props) {
  console.log(props);
  return axios.post('/api/auth', props)
    .then(response =>  {
      console.log(response);
      localStorage.setItem('token', response.data.access_token);
      return {
        type: LOGIN_SUCCESS,
        payload: response
      }})
    .catch(error => {
      console.log(error);
      return {
        type: LOGIN_FAILURE,
        payload: error
      }
    });
}

export function logoutAction() {
  localStorage.setItem('token', null);
  return {
    type: LOGOUT_ACTION
  }
}