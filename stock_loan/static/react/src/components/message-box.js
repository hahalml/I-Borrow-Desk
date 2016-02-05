import React from 'react';
import { Grid, Row, Col, Alert } from 'react-bootstrap';

export default ({ handleDismiss, message }) => {
  if (message.text) {
    return (
      <Grid>
        <Row>
          <Col md={6} xs={12} mdOffset={3}>
            <Alert
              bsStyle={message.type}
              closeLabel='Close'
              onDismiss={handleDismiss}>
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