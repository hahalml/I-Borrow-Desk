import React from 'react';
import { Table } from 'react-bootstrap';
import { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import Stock from './stock';
import { addWatchlist, removeWatchlist } from '../actions/index';

class StockTable extends Component {

  constructor(props) {
    super(props);
    this.state = { sort: 'fee' };
  }

  renderStock(stock) {
    const contains = this.props.watchlist.some(el => stock.symbol === el.symbol);
    const action = (contains) ? this.props.removeWatchlist : this.props.addWatchlist;
    const buttonType = (contains) ? 'remove' : 'add';

    return (
      <Stock
        key={stock.symbol + this.props.type}
        link={`/report/${stock.symbol}`}
        name={stock.name}
        symbol={stock.symbol}
        available={stock.available}a
        fee={stock.fee}
        updated={stock.datetime}
        buttonType={buttonType}
        handleClick={action}
        showUpdated={this.props.showUpdated}
      />
    );
  }

  sortStocks(stocks, key) {
    return stocks.sort((a, b) => b[key] - a[key]);
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
              {this.props.showUpdated && <th>Updated</th>}
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
  showUpdated: PropTypes.bool
};

const mapStateToProps = ({ watchlist }) => { return { watchlist }; };

export default connect(mapStateToProps, { addWatchlist, removeWatchlist })(StockTable);