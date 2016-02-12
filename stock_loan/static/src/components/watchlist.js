import React from 'react';
import { Component } from 'react';
import { Input } from 'react-bootstrap';
import { connect } from 'react-redux';

import { fetchWatchlist, toggleMorningEmail } from '../actions/index';
import StockTable from './stock-table';

class Watchlist extends Component {

  componentWillMount() {
    this.props.fetchWatchlist();
  }

  render() {
    const watchlist = this.props.watchlist;
    return (
      <div>
        <form>
          <Input
            type="checkbox"
            label='Receive Morning email'
            checked={this.props.auth.receiveEmail}
            onChange={this.props.toggleMorningEmail}
          />
        </form>
        <StockTable
            stocks={watchlist}
            showUpdated
        />
      </div>
    )
  }
}

const mapStateToProps = ({ watchlist, auth }) => {
  return { watchlist, auth }
};

export default connect(mapStateToProps,  { fetchWatchlist, toggleMorningEmail })(Watchlist);
