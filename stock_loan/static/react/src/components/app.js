import React from 'react';
import { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router';

import { logoutAction, showLoginAction, showPreferencesAction, clearMessage, fetchMostExpensive } from '../actions/index';
import NavBar from './nav-bar';
import Login from './login';
import Preferences from './preferences';
import MessageBox from './message-box';
import StockTable from './stock-table';

class App extends Component {

  componentDidMount() {
    this.props.fetchMostExpensive();
  }
  render() {
    return (
      <Grid>
        <Row>
          <NavBar
            authenticated={this.props.auth.authenticated}
            username={this.props.auth.username}
            onLogout={this.props.logoutAction}
            onClickLogin={this.props.showLoginAction}
            onClickPreferences={this.props.showPreferencesAction}
          />
          <hr />
          <Login show={this.props.auth.showLogin} />
          <Preferences show={this.props.auth.showPreferences} />
          {this.renderMessage()}
          {this.content()}
        </Row>
      </Grid>
    );
  }

  content() {
    if(this.props.children) {
      return this.props.children;
    } else {
      return (
        <div>
          <h2>Welcome to IBorrow Desk</h2>
          <p>If you haven't already, please consider <Link to='register'>registering!</Link>
            Registered users can maintain a watchlist, and receive (optional)
            morning updates. I'll also really appreciate it!
          </p>
          <h4>America's most expensive borrows</h4>
          <StockTable
            stocks={this.props.mostExpensive}
            type='fee'
            showUpdated />
        </div>
      );
    }
  }

  renderMessage() {
    if (this.props.message.text) {
      return (
        <MessageBox
          message={this.props.message}
          handleDismiss={this.props.clearMessage} />
      );
    }
  }
}

const mapStateToProps = state => {
  return {
    auth: state.auth,
    message: state.message,
    mostExpensive: state.mostExpensive
  }
};

export default connect(mapStateToProps,
  { logoutAction, showLoginAction, showPreferencesAction, clearMessage, fetchMostExpensive })
(App);