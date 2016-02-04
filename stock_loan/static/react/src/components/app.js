import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { logoutAction } from '../actions/index';
import NavBar from './nav-bar';

class App extends Component {
  render() {
    return (
      <div>
        <NavBar
          authenticated={this.props.auth.authenticated}
          onLogout={this.props.logoutAction}
        />
        {this.auth_failed()}
        {this.content()}
      </div>
    );
  }

  auth_failed() {
    if (this.props.auth.failure) {
      return <h1>You should login!</h1>;
    }
  }
  content() {if(this.props.children) {
      return this.props.children
    } else {
      return <h2>Time to Navigate</h2>
    }
  }
}

const mapStateToProps = state => {
  return {
    auth: state.auth
  }
};

export default connect(mapStateToProps, { logoutAction })(App);