import React from 'react';
import { Link } from 'react-router';

import utils from '../utils';

const renderDate = stock => {
  if (stock.datetime) {
    return <td>{stock.datetime}</td>;
  }

}

export default stock => {
  return (
    <Link to={stock.link}>
      <tr>
        <td>
            {stock.symbol}
        </td>
        <td>{stock.name}</td>
        <td>{utils.toPercentageNoScale(stock.fee)}</td>
        <td>{utils.toCommas(stock.available)}</td>
        {renderDate(stock)}
      </tr>
    </Link>
  )
}