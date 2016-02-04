import {  FETCH_STOCK, UPDATE_COMPANY_SEARCH, FETCH_TRENDING}
  from '../actions/index';
import { LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT_ACTION, AUTH_FAILURE }
  from '../actions/index';
import { FETCH_WATCHLIST } from '../actions/index';


export const StockReducer = (state={}, action) => {
  switch (action.type) {
    case FETCH_STOCK:
      return {...action.payload.data};
    default:
      return state;
  }
};

export const CompanySearchReducer = (state=[], action) => {
  switch(action.type) {
    case UPDATE_COMPANY_SEARCH:
      return action.payload.data.results;
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

export const AuthReducer = (state={authenticated: false, token: null, failure: false},
                            action) => {
  switch(action.type) {
    case LOGIN_SUCCESS:
      return {authenticated: true, token: action.payload.data.access_token, failure: false };
    case LOGOUT_ACTION:
      return {authenticated: false, token: null, failure: false};
    case AUTH_FAILURE:
      console.log('in auth reducer');
      return {authenticated: false, token: null, failure: true };
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
