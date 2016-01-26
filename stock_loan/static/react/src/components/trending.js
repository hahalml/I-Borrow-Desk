import React from 'react';
import { Component } from 'react';
import axios from 'axios';

import StockTable from './stock-table';

export default class extends Component {

  constructor(props) {
    super(props);
    this.state = {
      available: [],
      fee: []

    }
  }

  componentDidMount() {
    axios.get('/api/trending')
      .then(response => {
        this.setState({
          available: response.data.available,
          fee: response.data.fee
        })
      })
      .catch(response => console.log('error: ', response));
  }

  render () {

    if (this.state.available.length === 0) {
      return <h3>Loading...</h3>
    }

    return (
      <div>
        <div className="col-md-6">
          <h3> Declining Availability</h3>
          <StockTable stocks={this.state.available} />
        </div>
        <div className="col-md-6">
          <h3> Increasing Fee</h3>
          <StockTable stocks={this.state.fee} />
        </div>
      </div>
    )
  }

}