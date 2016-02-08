import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, compose, applyMiddleware, combineReducers } from 'redux';
import thunk from 'redux-thunk';
//import createHistory from 'history/lib/createHashHistory';
import { syncHistory, routeReducer } from 'redux-simple-router';
import { Router, Route, hashHistory } from 'react-router';
import { reducer as formReducer } from 'redux-form';

import App from './components/app';
import Trending from './components/trending';
import HistoricalReport from './components/historical-report';
import Watchlist from './components/watchlist';
import Login from './components/login';
import Register from './components/register';
import FilterStocks from './components/filter-stocks';

import {StockReducer, CompanySearchReducer, TrendingReducer, WatchlistReducer,
  AuthReducer, MessageReducer, FilteredStocksReducer, MostExpensiveReducer }
  from './reducers/index';


const middleware = syncHistory(hashHistory);
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
  compose(
    applyMiddleware(thunk, middleware),
    window.devToolsExtension ? window.devToolsExtension() : f => f
  )
);

middleware.listenForReplays(store);

ReactDOM.render(
  <Provider store={store}>
    <Router history={hashHistory}>
        <Route path='/' component={App}>
          <Route path='report/:ticker' component={HistoricalReport} />
          <Route path='trending' component={Trending} />
          <Route path='watchlist' component={Watchlist} />
          <Route path='register' component={Register} />
          <Route path='filter' component={FilterStocks} />
        </Route>
      </Router>
  </Provider>
  , document.querySelector('.container'));