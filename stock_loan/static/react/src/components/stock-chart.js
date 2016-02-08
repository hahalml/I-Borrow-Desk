import React from 'react';
import { LineChart, BarChart } from 'react-d3'
import d3 from 'd3';

import utils from '../utils';

const renderRow = (row) => {
  return (
    <tr key={row.time}>
      <td>{utils.toPercentage(row.fee)}</td>
      <td>{utils.toCommas(row.available)}</td>
      <td>{row.time}</td>
    </tr>
  )
};

const parseDateTime = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;
const parseDate = d3.time.format("%Y-%m-%d").parse;

export default ({ data, daily = false }) => {

  const parser = daily ? parseDate : parseDateTime;
  const feeData = [
    {
      'name': 'Fee',
      'values': data.map(row => {
        return {x: parser(row.time), y: row.fee};
      })
    }
  ];

  const availableData = [
    {
      'name': 'Available',
      'values': data.map(row => {
        return {x: parser(row.time), y: row.available};
      })
    }
  ];

  return (
    <div>
      <LineChart
        legend={true}
        data={feeData}
        width={800}
        height={300}
        viewBoxObject={{
          x: 0,
          y: 0,
          width: 800,
          height: 300
        }}
        title="Fee"
        yAxisLabel="Fee"
        xAxisLabel="Time"
        gridHorizontal={true}
      />
      <LineChart
        legend={true}
        data={availableData}
        width={800}
        height={300}
        viewBoxObject={{
          x: 0,
          y: 0,
          width: 800,
          height: 300
        }}
        title="Available"
        yAxisLabel="Available"
        xAxisLabel="Time"
        gridHorizontal={true}
      />
    </div>
  );
}
