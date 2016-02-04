import {  FETCH_STOCK, UPDATE_COMPANY_SEARCH, RESET_COMPANY_SEARCH, FETCH_TRENDING}
  from '../actions/index';
import { DAILY, REAL_TIME } from '../actions/index';
import { LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT_ACTION, SHOW_LOGIN, HIDE_LOGIN }
  from '../actions/index';
import { FETCH_WATCHLIST } from '../actions/index';


export const StockReducer = (state={}, action) => {
  switch (action.type) {
    case FETCH_STOCK:
      return {...action.payload.data, active: 'real_time'};
    case REAL_TIME:
      return {...state, active: 'real_time'};
    case DAILY:
      return {...state, active: 'daily'};
    default:
      return state;
  }
};

export const CompanySearchReducer = (state=[], action) => {
  switch(action.type) {
    case UPDATE_COMPANY_SEARCH:
      return action.payload.data.results;
    case RESET_COMPANY_SEARCH:
      return [];
  }
  return state;
};

export const TrendingReducer = (state={}, action) => {
  switch(action.type) {
    case FETCH_TRENDING:
      return {...action.payload.data};
    default:
      return state;
  }
};

export const AuthReducer =
  (state={ authenticated: false, token: null, showLogin: false, loginFailed: false},
   action) => {
  switch(action.type) {
    case LOGIN_SUCCESS:
      return {authenticated: true,
        token: action.payload.data.access_token,
        showLogin: false,
        loginFailed: false};
    case LOGIN_FAILURE:
      return {...state,
        authenticated: false,
        token: null,
        loginFailed: true};
    case LOGOUT_ACTION:
      return {authenticated: false,
        token: null,
        showLogin: false,
        loginFailed: false};
    case SHOW_LOGIN:
      return {authenticated: false,
        token: null,
        showLogin: true,
        loginFailed: false};
    case HIDE_LOGIN:
      return {...state, showLogin: false};
    default:
      return state
  }
};

export const WatchlistReducer = (state=[], action) => {
  switch(action.type) {
    case FETCH_WATCHLIST:
      return [...action.payload.data.watchlist];
    default:
      return state
  }
};
