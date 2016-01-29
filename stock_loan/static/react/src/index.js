import { createDevTools } from 'redux-devtools';
import LogMonitor from 'redux-devtools-log-monitor';
import DockMonitor from 'redux-devtools-dock-monitor';

import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, compose, applyMiddleware, combineReducers } from 'redux';
import ReduxPromise from 'redux-promise';
import createHistory from 'history/lib/createHashHistory';
import { syncHistory, routeReducer } from 'redux-simple-router';
import { Router, Route, browserHistory } from 'react-router';
import { reducer as formReducer } from 'redux-form';

import App from './components/app';
import Trending from './components/trending';
import HistoricalReport from './components/historical-report';
import Watchlist from './components/watchlist';
import Login from './components/login';

import {StockReducer, CompanySearchReducer, TrendingReducer, WatchlistReducer,
  AuthReducer }
  from './reducers/index';


const history = createHistory();
const middleware = syncHistory(history);
const reducer = combineReducers({
  routing: routeReducer,
  stock: StockReducer,
  companies: CompanySearchReducer,
  trending: TrendingReducer,
  form: formReducer,
  auth: AuthReducer,
  watchlist: WatchlistReducer
 });

const DevTools = createDevTools(
  <DockMonitor toggleVisibilityKey='ctrl-h'
               changePositionKey='ctrl-q'>
    <LogMonitor theme='tomorrow' />
  </DockMonitor>
);

const store = createStore(
  reducer,
  compose(
    applyMiddleware(middleware, ReduxPromise),
    DevTools.instrument()
  )
);

middleware.listenForReplays(store);

ReactDOM.render(
  <Provider store={store}>
    <div>
      <Router history={browserHistory}>
        <Route path='/' component={App}>
          <Route path='report/:ticker' component={HistoricalReport} />
          <Route path='trending' component={Trending} />
          <Route path='login' component={Login} />
          <Route path='watchlist' component={Watchlist} />
          </Route>
      </Router>
      <DevTools />
    </div>
  </Provider>
  , document.querySelector('.container'));