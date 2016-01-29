import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { fetchTrending }  from '../actions/index';
import StockTable from './stock-table';


class Trending extends Component {


  componentWillMount() {
    this.props.fetchTrending();
  }

  render() {

    const trending = this.props.trending;
    if (!trending.available) {
      return <h3>Loading...</h3>
    }

    return (
      <div>
        <div className="col-md-6">
          <h3> Declining Availability</h3>
          <StockTable stocks={trending.available} type='available'/>
        </div>
        <div className="col-md-6">
          <h3> Increasing Fee</h3>
          <StockTable stocks={trending.fee} type='fee' />
        </div>
      </div>
    )
  }

}

const mapStateToProps = ({ trending }) => {
  return { trending }
};

export default connect(mapStateToProps, { fetchTrending })(Trending);

