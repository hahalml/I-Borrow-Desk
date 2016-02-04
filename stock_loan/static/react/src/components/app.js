import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { logoutAction, showLoginAction } from '../actions/index';
import NavBar from './nav-bar';
import Login from './login';

class App extends Component {
  render() {
    return (
      <div>
        <NavBar
          authenticated={this.props.auth.authenticated}
          onLogout={this.props.logoutAction}
          onClickLogin={this.props.showLoginAction}
        />
        {this.login()}
        {this.content()}
      </div>
    );
  }

  login() {
    if (this.props.auth.showLogin) {
      return <Login />;
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

export default connect(mapStateToProps, { logoutAction, showLoginAction })(App);