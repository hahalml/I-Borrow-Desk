import React, { Component, PropTypes } from 'react';
import { Modal, ButtonInput, Input } from 'react-bootstrap';
import { reduxForm } from 'redux-form';

import utils from '../utils';
import { submitLogin, hideLoginAction } from '../actions/index';

class Login extends Component {

  render() {
    const { fields: { username, password }, handleSubmit } = this.props;
    return (
      <Modal show={true} onHide={() => this.props.hideLogin()}>
        <Modal.Header closeButton>
          <Modal.Title>Login</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={handleSubmit}>
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

export default reduxForm({
  form: 'LoginForm',
  fields: ['username', 'password'],
  validate,
  onSubmit: submitLogin
}, null, { hideLoginAction })(Login);