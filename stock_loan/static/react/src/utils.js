import React from 'react';
import { Input } from 'react-bootstrap';

const utils = {
  toPercentage: x => {
    return `${((x) * 100).toFixed(1)} %`;
  },

  toPercentageNoScale: x => {
    return `${x.toFixed(1)}%`;
  },

  toCommas: x => {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  },

  showWarning: (field) => {
    if (field.touched && field.invalid) return 'has-danger';
  },

  renderField: (field, label, type='text') => {
    return (
      <Input
        type={type}
        label={label}
        hasFeedback
        bsStyle={field.touched && field.error ? 'error' : 'success'}
        {...field}
        help={field.touched && field.error ? field.error : ''}
      />
    )
  }
};

export default utils;