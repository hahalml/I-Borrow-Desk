import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { removeWatchlist } from '../actions/index';
import StockTable from './stock-table';

class Watchlist extends Component {

  render() {
    const watchlist = this.props.watchlist;
    return (
      <StockTable
          stocks={watchlist}
          action={symbol => this.props.removeWatchlist(symbol)}
          buttonType='remove'
      />
    )
  }
}

const mapStateToProps = ({ watchlist }) => {
  return { watchlist }
};

export default connect(mapStateToProps, { removeWatchlist })(Watchlist);
