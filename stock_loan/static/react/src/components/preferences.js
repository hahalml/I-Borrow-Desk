import React, { Component, PropTypes } from 'react';
import { Modal } from 'react-bootstrap';
import { connect } from 'react-redux';

import { hidePreferencesAction } from '../actions/index';
import ChangeEmail from './change-email';
import ChangePassword from './change-password';

class Preferences extends Component {

  render() {
    return (
      <Modal show={this.props.show} onHide={this.props.hidePreferencesAction} >
        <Modal.Header closeButton>
          <Modal.Title>Preferences</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ChangeEmail />
          <ChangePassword />
        </Modal.Body>
      </Modal>
    )
  }
}

export default connect(null, { hidePreferencesAction })(Preferences);