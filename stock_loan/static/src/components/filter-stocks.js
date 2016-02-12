import React from 'react';
import { Component } from 'react';
import { Grid, Row, Col, ButtonInput, Input } from 'react-bootstrap';
import { connect } from 'react-redux';

import { addWatchlist }  from '../actions/index';
import StockTable from './stock-table';
import FilterSearchBar from './filter-search-bar';
import utils from '../utils';

class FilterStocks extends Component {

  render() {
    return (
      <div>
        <FilterSearchBar />
        <StockTable
          stocks={this.props.filteredStocks}
          action={symbol => this.props.addWatchlist(symbol)}
          buttonType='add'
          showUpdated
        />
      </div>
    );
  }
}

const mapStateToProps = ({ filteredStocks }) => {
  return { filteredStocks };
};

export default connect(mapStateToProps, { addWatchlist })(FilterStocks);


