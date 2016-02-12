import React from 'react';
import { Button } from 'react-bootstrap';
import { Link } from 'react-router';

import utils from '../utils';

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
      {props.showUpdated && <td>{props.updated}</td>}
      <td>
        <Button
          onClick={() => props.handleClick(props.symbol)}
          bsSize="xs"
          bsStyle={buttonClass}
        >
          {buttonText}
        </Button>
      </td>
    </tr>

  )
}