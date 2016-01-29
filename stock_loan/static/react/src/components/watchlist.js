import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import StockTable from './stock-table';

class Watchlist extends Component {

  render() {
    const watchlist = this.props.watchlist;
    return (
      <div>
        Watchlist
        <StockTable stocks={watchlist} />
      </div>
    )
  }
}

const mapStateToProps = ({ watchlist }) => {
  return { watchlist }
};

export default connect(mapStateToProps)(Watchlist);
