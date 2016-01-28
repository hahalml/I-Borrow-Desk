import {  FETCH_STOCK, UPDATE_COMPANY_SEARCH } from '../actions/index';

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
