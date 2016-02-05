import React, { Component } from 'react';
import { Navbar, Nav, NavItem, MenuItem, Row, Col } from 'react-bootstrap';
import { connect } from 'react-redux';
import { routeActions } from 'redux-simple-router';
import { bindActionCreators } from 'redux';
import { Link } from 'react-router';
import { LinkContainer } from 'react-router-bootstrap';

import SearchBar from './search-bar';

export default class NavBar extends Component {
  constructor(props) {
    super(props);
  }

  render() {

    return (
      <div>
        <Navbar>
          <Navbar.Header>
            <Navbar.Brand>
              <Link to='/'>IBorrowDesk</Link>
            </Navbar.Brand>
          </Navbar.Header>
          <Nav>
            <LinkContainer to='/trending'>
              <NavItem>Trending</NavItem>
            </LinkContainer>
            {this.props.authenticated &&
              <LinkContainer to='watchlist'>
                <NavItem>Watchlist</NavItem>
              </LinkContainer>
            }
            {!this.props.authenticated &&
              <NavItem onClick={() => this.props.onClickLogin()}>
                Login
              </NavItem>
            }
            {!this.props.authenticated &&
              <LinkContainer to='/register'>
                <NavItem>Register</NavItem>
              </LinkContainer>
            }
            {this.props.authenticated &&
              <NavItem href="#" onClick={() => this.props.onLogout()}>
                Logout
              </NavItem>
            }
          </Nav>
          </Navbar>
        <Row>
          <Col md={8} xs={12} mdOffset={2}>
            <SearchBar />
          </Col>
        </Row>
      </div>
    )
  }
}