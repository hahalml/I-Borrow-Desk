import {  UPDATE_COMPANY_SEARCH } from '../actions/index';

export const companySearchReducer = (state=[], action) => {
  switch(action.type) {
    case UPDATE_COMPANY_SEARCH:
      return action.payload.data.results;
  }
  return state;
};
