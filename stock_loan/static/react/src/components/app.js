import React from 'react';
import { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import { connect } from 'react-redux';
import { Link } from 'react-router';

import { logoutAction, showLoginAction, clearMessage, fetchMostExpensive,
  addWatchlist  } from '../actions/index';
import NavBar from './nav-bar';
import Login from './login';
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
            onLogout={this.props.logoutAction}
            onClickLogin={this.props.showLoginAction}
          />
          <hr />
          {this.login()}
          {this.renderMessage()}
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
            action={symbol => this.props.addWatchlist(symbol)}
            buttonType='add'
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
  { logoutAction, showLoginAction, clearMessage, fetchMostExpensive, addWatchlist })
(App);