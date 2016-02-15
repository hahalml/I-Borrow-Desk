import React from 'react';
import { Button } from 'react-bootstrap';
import { Link } from 'react-router';

import utils from '../utils';

export default props => {

  const buttonText = (props.buttonType === 'add') ?
    'Add' : 'Remove';
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
      <td style={{textAlign: 'right'}}>{utils.toPercentageNoScale(props.fee)}</td>
      <td style={{textAlign: 'right'}}>{utils.toCommas(props.available)}</td>
      {props.showUpdated && <td style={{textAlign: 'right'}}>{props.updated}</td>}
      <td style={{textAlign: 'center'}}>
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