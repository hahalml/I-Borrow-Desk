import React, { Component, PropTypes } from 'react';
import { Modal, ButtonInput, Input } from 'react-bootstrap';
import { reduxForm } from 'redux-form';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import utils from '../utils';

import { submitNewEmail } from '../actions/index';

class ChangeEmail extends Component {

  render() {
    const { fields: { password, email }, handleSubmit } = this.props;
    return (
      <Modal show={true} onHide={this.props.routeActions.goBack} >
        <Modal.Header closeButton>
          <Modal.Title>Change Email</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={(data) => handleSubmit(data).then(
          () => this.props.routeActions.goBack(), err => console.log(err))}>
            {utils.renderField(password, 'Password', 'password')}
            {utils.renderField(email, 'New Email')}
            <ButtonInput type="submit" value="Submit" />
          </form>
        </Modal.Body>
      </Modal>
    )
  }
}

function validate({ email, password }) {
  let errors = {};
  let emailRe = /\S+@\S+\.\S+/;

  if (!password) errors.password = 'Password required';
  if (!email) errors.email = 'Email address required';
  else if (!email.match(emailRe)) errors.email = 'Invalid Email Address';
  return errors;
}

const mapDispatchToProps = (dispatch) => {
  return {
    routeActions: bindActionCreators(routeActions, dispatch)
  }
};

export default reduxForm({
  form: 'EmailForm',
  fields: ['password', 'email'],
  validate,
  onSubmit: submitNewEmail,
  returnRejectedSubmitPromise : true
}, null, mapDispatchToProps)(ChangeEmail);