import React, { Component, PropTypes } from 'react';
import { reduxForm } from 'redux-form';

import { submitLogin, fetchWatchlist } from '../actions/index';

class Login extends Component {

  onSubmit(props){
    this.props.submitLogin(props)
      .then(() => this.props.fetchWatchlist());
  }

  render() {
    //console.log(this.props);
    const { fields: { username, password }, handleSubmit } = this.props;

    return (
      <form onSubmit={handleSubmit(this.onSubmit.bind(this))}>
        <h2> Login</h2>
        <input type="text" {...username} />
        <input type="password" {...password} />
        <button type="submit">Submit</button>
      </form>
  )
}

}

function validate(value) {
  return {};
}

export default reduxForm({
  form: 'LoginForm',
  fields: ['username', 'password']
}, null, { submitLogin, fetchWatchlist })(Login);