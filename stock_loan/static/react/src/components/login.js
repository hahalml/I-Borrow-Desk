import React, { Component, PropTypes } from 'react';
import { Modal, ButtonInput, Input } from 'react-bootstrap';
import { reduxForm } from 'redux-form';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import utils from '../utils';

import { submitLogin, fetchWatchlist, hideLoginAction } from '../actions/index';

class Login extends Component {

  render() {
    const { fields: { username, password }, handleSubmit } = this.props;
    return (
      <Modal show={true} onHide={() => this.props.hideLogin()}>
        <Modal.Header closeButton>
          <Modal.Title>Login</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={handleSubmit(this.props.submitLogin)}>
            {utils.renderField(username, 'Username')}
            {utils.renderField(password, 'Password', 'password')}
            <ButtonInput type="submit" value="Submit" />
          </form>
        </Modal.Body>
      </Modal>
    )
  }
}

function validate(values) {
  let errors = {};
  if (!values.username) errors.username = 'Username required';
  if (!values.password) errors.password = 'Password required';
  return errors;
}

const mapStateToProps = ({ auth }) => { return { auth };};

const mapDispatchToProps = (dispatch) => {
  return {
    submitLogin: bindActionCreators(submitLogin, dispatch),
    fetchWatchlist: bindActionCreators(fetchWatchlist, dispatch),
    routeActions: bindActionCreators(routeActions, dispatch),
    hideLogin: bindActionCreators(hideLoginAction, dispatch)
  }
};

export default reduxForm({
  form: 'LoginForm',
  fields: ['username', 'password'],
  validate
}, mapStateToProps, mapDispatchToProps)(Login);