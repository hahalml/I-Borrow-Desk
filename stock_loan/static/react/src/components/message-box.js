import React, { Component, PropTypes } from 'react';
import { Grid, Row, Col, Alert } from 'react-bootstrap';

export default class MessageBox extends Component {

  componentDidMount() {
    // Automatically hide the message box after 5s
    setTimeout(() => this.props.handleDismiss(), 5000);
  }

  render () {
    const message = this.props.message;
    if (message.text) {
      return (
        <Grid>
          <Row>
            <Col md={6} xs={12} mdOffset={3}>
              <Alert
                bsStyle={message.type}
                closeLabel='Close'
                onDismiss={this.props.handleDismiss}>
                {message.text}
              </Alert>
            </Col>
          </Row>
        </Grid>
      );
    }
    else {
      return <div></div>;
    }
  }
}

MessageBox.propTypes = {
  message : PropTypes.object,
  handleDismiss : PropTypes.func
};