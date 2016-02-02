import React, { Component, PropTypes } from 'react';
import { reduxForm } from 'redux-form';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import utils from '../utils';

import { submitLogin, fetchWatchlist } from '../actions/index';

class Login extends Component {

  onSubmit(props){
    console.log(this.props);
    this.props.submitLogin(props)
      .then(() => this.props.fetchWatchlist())
      .then(() => this.props.routeActions.push('/watchlist'));
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
      <form onSubmit={handleSubmit(this.onSubmit.bind(this))}>
        <h2> Login</h2>
        {this.renderField(username)}
        {this.renderField(password, 'password')}
        <button type="submit">Submit</button>
      </form>
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