import React, { Component } from 'react';
import { Navbar, Nav, NavDropdown, NavItem, MenuItem, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router';
import { LinkContainer } from 'react-router-bootstrap';

import SearchBar from './search-bar';

export default class NavBar extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Row>
        <Navbar>
          <Navbar.Header>
            <Navbar.Brand>
              <Link to='/'>IBorrowDesk</Link>
            </Navbar.Brand>
            <Navbar.Toggle />
          </Navbar.Header>
          <Navbar.Collapse>
            <Nav>
              <LinkContainer to='/trending'>
                <NavItem>Trending</NavItem>
              </LinkContainer>
              <LinkContainer to='/filter'>
                <NavItem>Filter</NavItem>
              </LinkContainer>
              <LinkContainer to='/about'>
                <NavItem>About</NavItem>
              </LinkContainer>
              <LinkContainer to='/changelog'>
                <NavItem>Changes</NavItem>
              </LinkContainer>
              <NavItem href="https://twitter.com/IBorrowDesk">
                @IBorrowDesk
              </NavItem>
              {this.props.authenticated &&
              <LinkContainer to='watchlist'>
                <NavItem>Watchlist</NavItem>
              </LinkContainer>}
            </Nav>
            <Nav pullRight>
              {this.props.authenticated &&
              <NavDropdown title={this.props.username || ''} id="nav-dropdown">
                <MenuItem href="#" onClick={() => this.props.onLogout()}>
                 Logout
                </MenuItem>
                <MenuItem onClick={this.props.onClickPreferences}>
                  Preferences
                </MenuItem>
              </NavDropdown>}
              {!this.props.authenticated &&
              <LinkContainer to='/register'>
                <NavItem>Register</NavItem>
              </LinkContainer>}
              {!this.props.authenticated &&
              <NavItem onClick={this.props.onClickLogin}>
                Login
              </NavItem>}
            </Nav>
          </Navbar.Collapse>
        </Navbar>
        <Row>
          <Col md={8} xs={12} mdOffset={2}>
            <SearchBar />
          </Col>
        </Row>
      </Row>

    )
  }
}