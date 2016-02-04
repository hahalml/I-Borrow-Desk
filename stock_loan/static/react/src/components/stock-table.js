import React from 'react';
import { Table } from 'react-bootstrap';
import { Component, PropTypes } from 'react';

import Stock from './stock';

export default class StockTable extends Component {

  constructor(props) {
    console.log(props);
    super(props);

    this.state = {
      sort: 'fee'
    }
  }

  renderStock(stock) {
    return (
      <Stock
        key={stock.symbol + this.props.type}
        link={`/report/${stock.symbol}`}
        name={stock.name}
        symbol={stock.symbol}
        available={stock.available}
        fee={stock.fee}
        buttonType={this.props.buttonType}
        onClick={this.props.action}
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
      <div>
        <Table condensed responsive hover>
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
        </Table>
      </div>
    );
  }
}

StockTable.propTypes = {
  stocks: PropTypes.array,
  action: PropTypes.function
};