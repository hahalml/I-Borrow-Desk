import axios from 'axios';
import React, { Component } from 'react';
import StockChart from '../components/stock-chart';

export default class HistoricalReport extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeTicker: {}
    };
  }

  componentDidMount() {
    this.updateTicker(this.props.params.ticker);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.params.ticker != this.props.params.ticker) {
      this.updateTicker(nextProps.params.ticker);
    }
  }

  updateTicker(ticker) {
    axios.get(`/api/ticker/${ticker}`)
      .then(response => {
        this.setState({activeTicker: response.data})
      })
      .catch(response => {
        console.log('error: ', response);
      });
  }

  render() {
  if (!this.state.activeTicker.name) return <div>Loading...</div>;
    const name = (this.state.activeTicker) ? this.state.activeTicker.name : 'NA';
    return (
      <div>
        <h2>{name}</h2>
        {this.renderStockChart()}
      </div>
    )
  }

  renderStockChart() {
    if (this.state.activeTicker) {
      return <StockChart data={this.state.activeTicker.real_time}/>;
    }
  }
}


