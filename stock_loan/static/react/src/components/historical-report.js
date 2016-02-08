if (typeof window.Promise !== 'function') {
  require('es6-promise').polyfill();
}


import React, { Component } from 'react';
import { Button, ButtonToolbar } from 'react-bootstrap';
import { connect } from 'react-redux';
import StockChart from './stock-chart';
import { fetchStock, addWatchlist, viewDaily, viewRealTime } from '../actions/index';

class HistoricalReport extends Component {

  componentWillMount() {
    this.props.fetchStock(this.props.params.ticker);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.params.ticker != this.props.params.ticker) {
      this.props.fetchStock(nextProps.params.ticker);
    }
  }

  render() {
    const { stock } = this.props;
    if (!stock.real_time) return <div>Loading...</div>;
    const data = (stock.active === 'real_time') ? stock.real_time : stock.daily;
    return (
      <div>
        <h2>
          {stock.name} - {stock.symbol}
          <ButtonToolbar>
            <Button
              onClick={() => this.props.viewRealTime()}
              bsStyle="success">
              Real-Time
            </Button>
            <Button
              onClick={() => this.props.viewDaily()}
              bsStyle="success">
              Daily
            </Button>
            <Button
              onClick={() => this.props.addWatchlist(stock.symbol)}
              bsStyle="success">
              Add to Watchlist
            </Button>
          </ButtonToolbar>
        </h2>
        <StockChart
          data={data}
          daily={stock.active === 'daily'}
        />
      </div>
    )
  }
}

const mapStateToProps = ({ stock }) => {
  return { stock }
};

export default connect(mapStateToProps,
  { fetchStock, addWatchlist, viewRealTime, viewDaily })
(HistoricalReport);
