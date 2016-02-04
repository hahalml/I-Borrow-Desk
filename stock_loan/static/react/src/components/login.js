import React, { Component, PropTypes } from 'react';
import { Modal } from 'react-bootstrap';
import { reduxForm } from 'redux-form';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import utils from '../utils';

import { submitLogin, fetchWatchlist } from '../actions/index';

class Login extends Component {

  onSubmit(props){
    this.props.submitLogin(props);
  }

  renderField(field, type='text') {
    return (
      <div className={`form-group ${utils.showWarning(field)}`}>
        <label>{field.name}</label>
        <input type={type} className="form-control" {...field} />
        <div className="text-help has-warning">
          {field.touched ? field.error: ''}
        </div>
      </div>
    )
  }

  render() {
    //console.log(this.props);
    const { fields: { username, password }, handleSubmit } = this.props;
    return (
      <Modal show={true}>
        <Modal.Header closeButton>
          <Modal.Title>Login</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={handleSubmit(this.onSubmit.bind(this))}>
            {this.renderField(username)}
            {this.renderField(password, 'password')}
            <button type="submit">Submit</button>
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

const mapDispatchToProps = (dispatch) => {
  return {
    submitLogin: bindActionCreators(submitLogin, dispatch),
    fetchWatchlist: bindActionCreators(fetchWatchlist, dispatch),
    routeActions: bindActionCreators(routeActions, dispatch)
  }
};

export default reduxForm({
  form: 'LoginForm',
  fields: ['username', 'password'],
  validate
}, null, mapDispatchToProps)(Login);