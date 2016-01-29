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
      <nav className="navbar navbar-default header">
        <div className="container-fluid">
          <Link to="/" className="navbar-brand">
            IBorrow
          </Link>
          <ul className="nav navbar-nav">
            <Link activeClassName="active" to={'trending'}>
              Trending
            </Link>
            {this.props.authenticated &&
              <Link activeClassName="active" to={'watchlist'}>
                Watchlist
              </Link>
            }

            {!this.props.authenticated &&
              <Link activeClassName="active" to={'login'}>
                Login
              </Link>
            }
            {this.props.authenticated &&
              <button
                onClick={() => this.props.onLogout()}
                className="btn btn-danger">
                Logout
              </button>
            }
          </ul>
          <SearchBar />
        </div>

      </nav>
    )
  }
}