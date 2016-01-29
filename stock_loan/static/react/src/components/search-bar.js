import React, { Component } from 'react';
import { connect } from 'react-redux';
import { routeActions } from 'redux-simple-router';
import { Combobox } from 'react-widgets';
import _ from 'lodash';

import { bindActionCreators } from 'redux';
import { searchCompany } from '../actions/index';

class SearchBar extends Component {

  constructor(props) {
    super(props);
    this.state = { ticker: '' };
    this.onInputChange = this.onInputChange.bind(this);
    this.onFormSubmit = this.onFormSubmit.bind(this);
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

  onFormSubmit(event) {
    event.preventDefault();
    // navigate to new url
    const ticker = this.state.ticker;
    this.setState({ ticker: '' });
    this.props.routeActions.push(`/report/${ticker}`);
  }

  optionClicked(value) {
    const ticker = value.symbol;
    this.setState({ ticker: '' });
    this.props.routeActions.push(`/report/${ticker}`);
  }

  render() {
    const companies = this.props.companySearch.map( el => {
      return {'symbol': el.symbol, 'name': `${el.name} - ${el.symbol}`};
    });
    return (
      <form
        onSubmit={this.onFormSubmit}
        className="navbar-form navbar-right"
      >
        <div className="form-group">
          <Combobox
            data={companies}
            suggest={true}
            valueField='symbol'
            textField='name'
            placeholder="Search a ticker"
            className="form-control"
            value={this.state.ticker}
            onChange={this.onInputChange}
            onSelect={this.optionClicked.bind(this)}
          />
          <button type="submit" className="btn btn-secondary">Submit</button>
        </div>
      </form>
    );
  }
}

const mapStateToProps = (state) => {
  return { companySearch: state.companies }
};

const mapDispatchToProps = (dispatch) => {
  return {
    searchCompany: bindActionCreators(searchCompany, dispatch),
    routeActions: bindActionCreators(routeActions, dispatch)
  }
};

export default connect(mapStateToProps, mapDispatchToProps)(SearchBar);