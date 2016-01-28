
import React from 'react';
import { Component } from 'react';

import NavBar from './nav-bar';

export default class App extends Component {
  render() {
    return (
      <div>
        <NavBar />
        {this.content()}
      </div>
    );
  }

  content() {if(this.props.children) {
      return this.props.children
    } else {
      return <h2>Time to Navigate</h2>
    }
  }
}