import React, { Component } from 'react';
import { connect } from 'react-redux';
import StockChart from './stock-chart';
import { fetchStock } from '../actions/index';

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
