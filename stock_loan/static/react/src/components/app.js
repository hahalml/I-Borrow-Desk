import React from 'react';
import { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import { connect } from 'react-redux';

import { logoutAction, showLoginAction, clearMessage  } from '../actions/index';
import NavBar from './nav-bar';
import Login from './login';
import MessageBox from './message-box';

class App extends Component {
  render() {
    return (
      <Grid>
        <Row>
          <NavBar
            authenticated={this.props.auth.authenticated}
            onLogout={this.props.logoutAction}
            onClickLogin={this.props.showLoginAction}
          />
          <hr />
          {this.login()}
          <MessageBox
            message={this.props.message}
            handleDismiss={this.props.clearMessage}
          />
          {this.content()}
        </Row>
      </Grid>
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
    auth: state.auth,
    message: state.message
  }
};

export default connect(mapStateToProps,
  { logoutAction, showLoginAction, clearMessage })(App);