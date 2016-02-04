import React from 'react';
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
    'btn btn-sm btn-success' : 'btn btn-sm btn-danger';

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
        <button
          onClick={() => {
            console.log('clicked' + props.symbol);
            props.onClick(props.symbol);
          }}
          className={buttonClass}
        >
          {buttonText}
        </button>
      </td>
    </tr>

  )
}