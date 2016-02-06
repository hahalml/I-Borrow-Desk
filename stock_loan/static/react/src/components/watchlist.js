import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { removeWatchlist, fetchWatchlist } from '../actions/index';
import StockTable from './stock-table';

class Watchlist extends Component {

  componentWillMount() {
    this.props.fetchWatchlist();
  }

  render() {
    const watchlist = this.props.watchlist;
    return (
      <StockTable
          stocks={watchlist}
          action={symbol => this.props.removeWatchlist(symbol)}
          buttonType='remove'
          showUpdated
      />
    )
  }
}

const mapStateToProps = ({ watchlist }) => {
  return { watchlist }
};

const mapDispatchToProps = dispatch => {
  return {
    fetchWatchlist: bindActionCreators(fetchWatchlist, dispatch),
    removeWatchlist: bindActionCreators(removeWatchlist, dispatch)
  };
};

export default connect(mapStateToProps,  mapDispatchToProps)(Watchlist);
