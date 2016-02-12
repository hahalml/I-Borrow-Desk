import React, { Component, PropTypes } from 'react';
import { ButtonInput, Alert } from 'react-bootstrap';
import { reduxForm } from 'redux-form';

import utils from '../utils';
import { submitNewEmail } from '../actions/index';

class ChangeEmail extends Component {

  constructor(props) {
    super(props);
    this.state = {message: ''}
  }

  render() {
    const { fields: { password, email }, handleSubmit } = this.props;
    return (
      <div>
        <h4>Change Email Address</h4>
        <form onSubmit={(data) => handleSubmit(data).then(
        () => this.setState({message: 'Email successfully changed!'}), err => console.log(err))}>
          {utils.renderField(password, 'Re-enter Password', 'password')}
          {utils.renderField(email, 'New Email')}
          <ButtonInput type="submit" value="Submit" />
        </form>
        {this.state.message &&
        <Alert bsStyle="success" onDismiss={() => this.setState({message: ''})}>
          {this.state.message}
        </Alert>}
      </div>
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


export default reduxForm({
  form: 'EmailForm',
  fields: ['password', 'email'],
  validate,
  onSubmit: submitNewEmail,
  returnRejectedSubmitPromise : true
})(ChangeEmail);