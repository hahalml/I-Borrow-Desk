import React, { Component, PropTypes } from 'react';
import { Grid, Row, Col, ButtonInput, Input } from 'react-bootstrap';
import { reduxForm } from 'redux-form';

import { submitFilter } from '../actions/index';

const COUNTRIES = ['USA', 'Canada', 'Australia', 'Austria', 'Belgium', 'British', 'Dutch',
  'France', 'Germany', 'HongKong', 'India', 'Italy', 'Japan', 'Mexico', 'Spain',
  'Swedish', 'Swiss'];
const ORDER_OPTIONS = ['fee', 'available'];

const INITIAL_VALUES = {min_available: 0, max_available: 100000,
  min_fee: 0, max_fee: 100, country: 'USA', order_by: 'fee'};

class Filter extends Component {

  renderField(field, label) {
    return (
      <Input
        type='number'
        label={label}
        bsStyle={field.invalid ? 'error' : 'success'}
        help={field.touched && field.invalid ? field.error : ''}
        {...field}
      />
    )
  }

  render() {
    const {fields: {min_available, max_available, min_fee, max_fee, country, order_by },
      resetForm, handleSubmit } = this.props;

    return (
      <Grid>
        <form onSubmit={handleSubmit}>
          <Row>
            <Col xs={12} md={4}>
              {this.renderField(min_available, 'Minimum Available')}
              {this.renderField(min_fee, 'Minimum Fee (%)')}
            </Col>
            <Col xs={12} md={4}>
              {this.renderField(max_available, 'Maximum Available')}
              {this.renderField(max_fee, 'Maximum Fee (%)')}
            </Col>
            <Col xs={12} md={4}>
              <Input type="select" label="Country" {...country}>
                {COUNTRIES.map(country => {
                  return (<option value={country} key={country}>
                    {country}
                  </option>);})}
              </Input>
              <Input type="select" label="Order By" {...order_by}>
                {ORDER_OPTIONS.map(order => {
                return (<option value={order} key={order}>
                  {order}
                  </option>);})}
              </Input>
            </Col>
          </Row>
          <Row>
            <ButtonInput type="submit" value="Submit" />
          </Row>
        </form>
      </Grid>
    )
  }
}

const validate = ({ min_available, max_available, min_fee, max_fee }) => {
  let errors = {};

  if (max_available <= min_available) {
    errors.min_available = 'Must be less than Maximum';
    errors.max_available = 'Must be greater than Minimum';
  }
  if (max_fee <= min_fee) {
    errors.min_fee = 'Must be less than Maximum';
    errors.max_fee = 'Must be greater than Minimum';
  }
  if (min_available < 0) errors.min_available = 'Must be positive.';
  if (max_available < 0) errors.max_available = 'Must be positive.';
  if (min_fee < 0) errors.min_fee = 'Must be positive.';
  if (max_fee < 0) errors.max_fee = 'Must be positive.';
  return errors;
};

export default reduxForm({
  form: 'FilterForm',
  fields: ['min_available', 'max_available', 'min_fee', 'max_fee', 'country', 'order_by'],
  validate,
  destroyOnUnmount: false,
  onSubmit: submitFilter
}, state => ({ initialValues: INITIAL_VALUES}))(Filter);