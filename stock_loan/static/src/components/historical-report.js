import React, { Component } from 'react';
import { Button, Table, Col } from 'react-bootstrap';
import { connect } from 'react-redux';

import StockChart from './stock-chart';
import { fetchStock, addWatchlist, removeWatchlist } from '../actions/index';
import  utils from '../utils';

class HistoricalReport extends Component {

  componentWillMount() {
    this.props.fetchStock(this.props.params.ticker);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.params.ticker != this.props.params.ticker) {
      this.props.fetchStock(nextProps.params.ticker);
    }
  }

  renderTable(data) {
    data.reverse();
    return (
      <Col md={4} mdOffset={4} >
        <h3>Recent Data</h3>
        <Table condensed responsive hover>
          <thead>
            <tr>
              <th>Fee</th>
              <th>Available</th>
              <th align="right">Updated</th>
            </tr>
          </thead>
          <tbody>
            {data.map(el =>
              (<tr key={el.time}>
                <td>{utils.toPercentage(el.fee)}</td>
                <td>{utils.toCommas(el.available)}</td>
                <td>{el.time.replace("T", " ")}</td>
              </tr>)
            )}
          </tbody>
        </Table>
      </Col>
    )
  }

  render() {
    const { stock } = this.props;
    if (!stock.name) return <div>Loading...</div>;
    const contains = this.props.watchlist && this.props.watchlist.some(el => stock.symbol === el.symbol);
    const action = contains ? this.props.removeWatchlist : this.props.addWatchlist;
    const data = stock.daily;
    return (
      <div>
        <h2>
          {stock.name} - {stock.symbol}
        </h2>
          <Button
            onClick={() => action(stock.symbol)}
            bsStyle={contains ? "danger" : "success"}>
            {contains ? "Remove from Watchlist" : "Add to Watchlist"}
          </Button>
        <StockChart
          data={data}
          daily={true}
        />
        {stock.real_time && this.renderTable(stock.real_time)}
      </div>
    )
  }
}

const mapStateToProps = ({ stock, watchlist }) => {
  return { stock, watchlist }
};

export default connect(mapStateToProps,
  { fetchStock, addWatchlist, removeWatchlist })
(HistoricalReport);
