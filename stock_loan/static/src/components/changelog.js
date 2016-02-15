import React from 'react';
import { ListGroup, ListGroupItem } from 'react-bootstrap';

export default () => {
  return (
    <ListGroup>
      <ListGroupItem>February 14, 2016 - New URL! www.iborrowdesk.com</ListGroupItem>
      <ListGroupItem>February, 2016 - New Features: Universal search box, better charting
        with <a href="https://rrag.github.io/react-stockcharts/">React Stockcharts</a>,
        snappier navigation and more dynamic UI in general.</ListGroupItem>
      <ListGroupItem>January, 2016 - Begin rebuilding the front-end with React</ListGroupItem>
      <ListGroupItem>October 13, 2015 - Update backend schema. Report generation speedup by several ordes of magnitude</ListGroupItem>
      <ListGroupItem>October 6, 2015 - Graphs of historical data now available with <a href="http://dimplejs.org/">
        dimple</a></ListGroupItem>
      <ListGroupItem>September 15, 2015 - Include stock prices in subscriber morning emails</ListGroupItem>
      <ListGroupItem>August 24, 2015 - Trending tickers (rising fees, falling availability) now provided</ListGroupItem>
      <ListGroupItem>August 17, 2015 - Fuzzy name search for companies now supported</ListGroupItem>
      <ListGroupItem>August 9, 2015 - Front-end rebuilt</ListGroupItem>
      <ListGroupItem>August 1, 2015 - Backend ported to Python 3</ListGroupItem>
      <ListGroupItem>July 13, 2015 - Filtering functionality added</ListGroupItem>
      <ListGroupItem>July 2015 - Site and Twitter bot launch</ListGroupItem>
    </ListGroup>
  )
}