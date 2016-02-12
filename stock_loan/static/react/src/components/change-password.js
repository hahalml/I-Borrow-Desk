import React, { Component, PropTypes } from 'react';
import { ButtonInput, Alert } from 'react-bootstrap';
import { reduxForm } from 'redux-form';

import utils from '../utils';
import { submitNewPassword } from '../actions/index';

class ChangeEmail extends Component {

  constructor(props) {
    super(props);
    this.state = {message: ''}
  }

  render() {
    const { fields: { password, newPassword, confirmPassword }, handleSubmit } = this.props;
    return (
      <div>
        <h4>Change Password</h4>
        <form onSubmit={(data) => handleSubmit(data).then(
        () => this.setState({message: 'Password successfully changed!'}),
        err => console.log(err))}>
          {utils.renderField(password, 'Re-enter Password', 'password')}
          {utils.renderField(newPassword, 'New Password', 'password')}
          {utils.renderField(confirmPassword, 'Confirm New Password', 'password')}
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

function validate({ password, newPassword, confirmPassword }) {
  let errors = {};

  if (!password) errors.password = 'Password required';
  if (!newPassword) errors.newPassword = 'New Password required';
  else if (newPassword.length < 6) errors.newPassword = 'Password must be at least 6 characters.';
  if (newPassword != confirmPassword) errors.confirmPassword = 'Password must match';
  return errors;
}


export default reduxForm({
  form: 'NewPasswordForm',
  fields: ['password', 'newPassword', 'confirmPassword'],
  validate,
  onSubmit: submitNewPassword,
  returnRejectedSubmitPromise : true
})(ChangeEmail);