if (typeof window.Promise !== 'function') {
 require('es6-promise').polyfill();
}
require("./css/style.css");

import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, compose, applyMiddleware, combineReducers } from 'redux';
import thunk from 'redux-thunk';
import { syncHistory, routeReducer } from 'redux-simple-router';
import { Router, Route, browserHistory } from 'react-router';
import { reducer as formReducer } from 'redux-form';

import { fetchProfile, fetchWatchlist } from './actions/index';

import App from './components/app';
import Trending from './components/trending';
import HistoricalReport from './components/historical-report';
import Watchlist from './components/watchlist';
import Register from './components/register';
import FilterStocks from './components/filter-stocks';
import About from './components/about';
import ChangeLog from './components/changelog';

import {StockReducer, CompanySearchReducer, TrendingReducer, WatchlistReducer,
  AuthReducer, MessageReducer, FilteredStocksReducer, MostExpensiveReducer }
  from './reducers/index';



const middleware = syncHistory(browserHistory);
const reducer = combineReducers({
  routing: routeReducer,
  stock: StockReducer,
  companies: CompanySearchReducer,
  trending: TrendingReducer,
  form: formReducer,
  auth: AuthReducer,
  watchlist: WatchlistReducer,
  message: MessageReducer,
  filteredStocks: FilteredStocksReducer,
  mostExpensive: MostExpensiveReducer
 });

const store = createStore(
  reducer,
  (sessionStorage.token) ? { auth: {authenticated: true, showLogin: false }} : {},
  compose(
    applyMiddleware(thunk, middleware),
    window.devToolsExtension ? window.devToolsExtension() : f => f
  )
);

middleware.listenForReplays(store);

if (store.getState().auth.authenticated) {
  store.dispatch(fetchProfile());
  store.dispatch(fetchWatchlist());
}

ReactDOM.render(
  <Provider store={store}>
    <div>
      <Router history={browserHistory}>
        <Route path='/' component={App}>
          <Route path='report/:ticker' component={HistoricalReport} />
          <Route path='trending' component={Trending} />
          <Route path='watchlist' component={Watchlist} />
          <Route path='register' component={Register} />
          <Route path='filter' component={FilterStocks} />
          <Route path='about' component={About} />
          <Route path='changelog' component={ChangeLog} />
        </Route>
      </Router>
    </div>
  </Provider>
  , document.querySelector('.container'));