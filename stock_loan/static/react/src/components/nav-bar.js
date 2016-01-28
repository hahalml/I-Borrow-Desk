import React, { Component } from 'react';
import { connect } from 'react-redux';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import { Link } from 'react-router';

import SearchBar from './../containers/search-bar';

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
          </ul>
          <SearchBar />
        </div>

      </nav>
    )
  }
}