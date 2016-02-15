import React from 'react';
import { Table, Glyphicon } from 'react-bootstrap';
import { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import Stock from './stock';
import { addWatchlist, removeWatchlist } from '../actions/index';

class StockTable extends Component {

  constructor(props) {
    super(props);
    this.state = { sort: 'fee', asc: true };
  }

  renderStock(stock) {
    const contains = this.props.watchlist.some(el => stock.symbol === el.symbol);
    const action = contains ? this.props.removeWatchlist : this.props.addWatchlist;
    const buttonType = contains ? 'remove' : 'add';

    return (
      <Stock
        key={stock.symbol + this.props.type}
        link={`/report/${stock.symbol}`}
        name={stock.name}
        symbol={stock.symbol}
        available={stock.available}a
        fee={stock.fee}
        updated={stock.datetime.replace('GMT', '')}
        buttonType={buttonType}
        handleClick={action}
        showUpdated={this.props.showUpdated}
      />
    );
  }

  sortStocks(stocks, key, asc) {
    return stocks.sort((a, b) => {
      let x = a[key];
      let y = b[key];
      if (typeof x == "string") {
          x = x.toLowerCase();
          y = y.toLowerCase();
      }
      if (asc) {
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
      } else {
        return ((x < y) ? 1 : ((x > y) ? -1 : 0));
      }
    });
  }

  setSort(key) {
    if (this.state.sort === key) {
      this.setState({ asc: !this.state.asc});
    } else {
      this.setState({sort: key, asc: true});
    }
  }


  render() {
    const stocks = this.sortStocks(this.props.stocks, this.state.sort, this.state.asc);

    return (
      <Table condensed responsive hover>
        <thead>
          <tr style={{cursor: 'pointer'}}>
            <th onClick={this.setSort.bind(this, 'symbol')}>Symbol <Glyphicon glyph="sort" /></th>
            <th onClick={this.setSort.bind(this, 'name')}>Name<Glyphicon glyph="sort" /></th>
            <th style={{textAlign: 'right'}}
                onClick={this.setSort.bind(this, 'fee')}>
              Fee<Glyphicon glyph="sort" />
            </th>
            <th style={{textAlign: 'right'}}
                onClick={this.setSort.bind(this, 'available')}>
              Availability<Glyphicon glyph="sort" />
            </th>
            {this.props.showUpdated && <th style={{textAlign: 'right'}}>Updated (EST)</th>}
            <th style={{textAlign: 'center'}}>Watchlist</th>
          </tr>
        </thead>
        <tbody data-link="row" className="rowlink">
          {stocks.map(stock => this.renderStock(stock))}
        </tbody>
      </Table>
    );
  }
}

StockTable.propTypes = {
  stocks: PropTypes.array,
  watchlist: PropTypes.array,
  showUpdated: PropTypes.bool,
  addWatchlist: PropTypes.func,
  removeWatchlist: PropTypes.func
};

const mapStateToProps = ({ watchlist }) => { return { watchlist }; };

export default connect(mapStateToProps, { addWatchlist, removeWatchlist })(StockTable);