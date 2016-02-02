import React, { Component } from 'react';
import { connect } from 'react-redux';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import { Link } from 'react-router';

import SearchBar from './search-bar';

export default class NavBar extends Component {
  constructor(props) {
    super(props);
  }

  render() {

    return (
      <div>
        <nav className="navbar navbar-default">
          <div className="container-fluid">
            <div className="collapse navbar-collapse">
            <Link to="/" className="navbar-brand">
              IBorrow
            </Link>
            <ul className="nav navbar-nav">
              <li>
                <Link activeClassName="active" to={'trending'}>
                  Trending
                </Link>
              </li>
              {this.props.authenticated &&
                <li>
                  <Link activeClassName="active" to={'watchlist'}>
                    Watchlist
                  </Link>
                </li>
              }
            </ul>
              <ul className="nav navbar-nav navbar-right">
              {!this.props.authenticated &&
                <li>
                  <Link activeClassName="active" to={'login'}>
                    Login
                  </Link>
                </li>
              }
              {this.props.authenticated &&
                <li>
                  <a href="#"
                    onClick={() => this.props.onLogout()}
                    >
                    Logout
                  </a>
                </li>
              }
            </ul>
          </div>
          </div>
        </nav>
        <SearchBar />
      </div>
    )
  }
}