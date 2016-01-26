import React from 'react';
import { Component } from 'react';

import Stock from './stock';

export default class extends Component {

  constructor(props) {
    super(props);
    this.state = {
      sort: 'fee'
    }
  }

  renderStock(stock) {
    return (
      <Stock
        key={stock.symbol}
        link={`/report/${stock.symbol}`}
        name={stock.name}
        symbol={stock.symbol}
        available={stock.available}
        fee={stock.fee}
      />
    );
  }

  sortStocks(stocks, key) {
    return stocks.sort((a, b) => b[key] - a[key])
  }

  setSort(key) {
    this.setState({ sort: key });
  }


  render() {
    const stocks = this.sortStocks(this.props.stocks, this.state.sort);

    return (
      <table className="table table-condensed table-responsive table-hover">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Name</th>
            <th onClick={this.setSort.bind(this, 'fee')}>Fee</th>
            <th onClick={this.setSort.bind(this, 'available')}>Availability</th>
          </tr>
        </thead>
        <tbody data-link="row" className="rowlink">
        {stocks.map(stock => this.renderStock(stock))}
        </tbody>
      </table>
    );
  }
}