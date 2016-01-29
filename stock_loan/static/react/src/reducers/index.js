import {  FETCH_STOCK, UPDATE_COMPANY_SEARCH, FETCH_TRENDING, FETCH_WATCHLIST }
  from '../actions/index';
import { LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT_ACTION }
  from '../actions/index';


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
      return state.concat(action.payload.data.results);
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

export const AuthReducer = (state={authenticated: false, token: null}, action) => {
  switch(action.type) {
    case LOGIN_SUCCESS:
      return {authenticated: true, token: action.payload.data.access_token };
    case LOGOUT_ACTION:
      return {authenticated: false, token: null};
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