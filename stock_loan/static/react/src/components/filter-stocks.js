import React from 'react';
import { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import { connect } from 'react-redux';

import { addWatchlist }  from '../actions/index';
import StockTable from './stock-table';

class FilterStocks extends Component {

  render() {
    return (
      <div>
        Filter stock table
      </div>
    );
  }
}

const mapStateToProps = ({ filteredStocks }) => {
  return { filteredStocks };
};

export default connect(mapStateToProps())(FilterStocks);


