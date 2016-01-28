import axios from 'axios';

export const UPDATE_COMPANY_SEARCH = 'UPDATE_COMPANY_SEARCH';
export const FETCH_STOCK = 'FETCH_STOCK';

export const searchCompany = name => {
  const url = `api/company/${name}`;
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