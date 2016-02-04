import React, { Component } from 'react';
import { connect } from 'react-redux';
import { routeActions } from 'redux-simple-router';
import { Combobox } from 'react-widgets';
import _ from 'lodash';

import { bindActionCreators } from 'redux';
import { searchCompany, resetCompanySearch } from '../actions/index';

class SearchBar extends Component {

  constructor(props) {
    super(props);
    this.state = { ticker: '' };
    this.onInputChange = this.onInputChange.bind(this);
    this.nameSearch = _.debounce(value => this.props.searchCompany(value), 300);
  }

  onInputChange(value) {
    if (typeof value === 'object') {
      this.setState({ticker: value.symbol});
    } else {
      this.setState({ticker: value});
      if (value.length > 2) this.nameSearch(value);
    }
  }

  optionClicked(value) {
    const ticker = value.symbol;
    this.setState({ ticker: '' });
    this.props.resetCompanySearch();
    this.props.routeActions.push(`/report/${ticker}`);
  }

  render() {
    const companies = this.props.companySearch.map( el => {
      return {'symbol': el.symbol, 'name': `${el.name} - ${el.symbol}`};
    });
    return (
      <Combobox
        data={companies}
        suggest={true}
        valueField='symbol'
        textField='name'
        placeholder="Search a ticker"
        value={this.state.ticker}
        onChange={this.onInputChange}
        onSelect={this.optionClicked.bind(this)}
      />
    );
  }
}

const mapStateToProps = (state) => {
  return { companySearch: state.companies }
};

const mapDispatchToProps = (dispatch) => {
  return {
    searchCompany: bindActionCreators(searchCompany, dispatch),
    resetCompanySearch: bindActionCreators(resetCompanySearch, dispatch),
    routeActions: bindActionCreators(routeActions, dispatch)
  }
};

export default connect(mapStateToProps, mapDispatchToProps)(SearchBar);