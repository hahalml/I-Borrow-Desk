import React from 'react';
import { Button } from 'react-bootstrap';
import { Link } from 'react-router';

import utils from '../utils';

const renderDate = stock => {
  if (stock.datetime) {
    return <td>{stock.datetime}</td>;
  }
};

export default props => {

  const buttonText = (props.buttonType === 'add') ?
    'Add to Watchlist' : 'Remove from Watchlist';
  const buttonClass = (props.buttonType === 'add') ?
    'success' : 'danger';

  return (
    <tr>
      <td>
        <Link to={props.link}>
          {props.symbol}
        </Link>
      </td>
      <td>{props.name}</td>
      <td>{utils.toPercentageNoScale(props.fee)}</td>
      <td>{utils.toCommas(props.available)}</td>
      <td>
        <Button
          onClick={() => {
            console.log('clicked' + props.symbol);
            props.onClick(props.symbol);
          }}
          bsSize="small"
          bsStyle={buttonClass}
        >
          {buttonText}
        </Button>
      </td>
    </tr>

  )
}