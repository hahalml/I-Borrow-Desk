import React, { Component } from 'react';
import { connect } from 'react-redux';
import StockChart from './stock-chart';
import { fetchStock } from '../actions/index';

class HistoricalReport extends Component {

  componentWillMount() {
    this.props.fetchStock(this.props.params.ticker);
  }

  render() {
    const stock = this.props.stock;
    if (!stock.name) return <div>Loading...</div>;
    return (
      <div>
        <h2>{stock.name} - {stock.symbol}</h2>
        <StockChart data={stock.real_time} />
      </div>
    )
  }
}

const mapStateToProps = ({ stock }) => {
  return { stock }
};

export default connect(mapStateToProps, { fetchStock })(HistoricalReport);
