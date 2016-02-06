import React, { Component, PropTypes } from 'react';
import { Grid, Row, Col, ButtonInput, Input } from 'react-bootstrap';
import { reduxForm } from 'redux-form';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import utils from '../utils';

import { submitRegister } from '../actions/index';

class Register extends Component {

  render() {
    const {fields: {username, email, password, confirmPassword, receiveEmail},
      resetForm, handleSubmit } = this.props;
    return (
      <Grid>
        <Row>
          <Col xs={12} md={6} mdOffset={3}>
            <h4>Register to maintain a watchlist and receive morning updates!</h4>
            <form onSubmit={handleSubmit(this.props.submitRegister)}>
              {utils.renderField(username, 'Username')}
              {utils.renderField(email, 'Email')}
              {utils.renderField(password, 'Password', 'password')}
              {utils.renderField(confirmPassword, 'Confirm Password', 'password')}
              <Input
                type='checkbox'
                label='Receive Morning Email'
                defaultChecked
                {...receiveEmail}
              />
              <ButtonInput type="submit" value="Register" />
            </form>
          </Col>
        </Row>
      </Grid>
    );
  }
}

const validate = ({ username, password, confirmPassword, email }) => {
  let errors = {};
  let emailRe = /\S+@\S+\.\S+/;

  if (!username) errors.username = 'Username required';
  else if (username.length < 6) errors.username = 'Username must be at least 6 characters.';

  if (!password) errors.password = 'Password required';
  else if (password.length < 6) errors.password = 'Password must be at least 6 characters.';
  if (password != confirmPassword) errors.confirmPassword = 'Password must match';

  if (!email) errors.email = 'Email address required';
  else if (!email.match(emailRe)) errors.email = 'Invalid Email Address';

  return errors;
};

const mapDispatchToProps = (dispatch) => {
  return { submitRegister: bindActionCreators(submitRegister, dispatch) };
};

export default reduxForm({
  form: 'RegisterForm',
  fields: ['username', 'password', 'confirmPassword', 'email', 'receiveEmail'],
  validate
}, null, mapDispatchToProps)(Register);