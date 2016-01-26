import axios from 'axios';

export const UPDATE_COMPANY_SEARCH = 'UPDATE_COMPANY_SEARCH';

export const searchCompany = name => {
  const url = `api/company/${name}`;
  const request = axios.get(url);
  return {
    type: UPDATE_COMPANY_SEARCH,
    payload: request
  };
};