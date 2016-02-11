import React, { Component } from 'react';
import ReStock from 'react-stockcharts';
import d3 from 'd3';

const { ChartCanvas, Chart, DataSeries, EventCapture } = ReStock;
const { AreaSeries, HistogramSeries, LineSeries } = ReStock.series;
const { XAxis, YAxis} = ReStock.axes;
const { fitWidth, TypeChooser } = ReStock.helper;
const { StockscaleTransformer } = ReStock.transforms;
const { MouseCoordinates } = ReStock.coordinates;
const { TooltipContainer, SingleValueTooltip } = ReStock.tooltip;

class StockChart extends Component {
  render() {

    const { data, daily, width } = this.props;
    const parseDate = daily
      ? d3.time.format("%Y-%m-%d").parse
      : d3.time.format("%Y-%m-%dT%H:%M:%S").parse;


    const parsedData = data.map(el => {
      let parsed = {};
      parsed.fee = el.fee;
      parsed.available = el.available;
      parsed.date = new Date(parseDate(el.time).getTime());
      return parsed;
    });

    return (
      <ChartCanvas
        width={width}
        height={600}
        margin={{left: 80, right: 50, top:60, bottom: 30}}
        dataTransform={[ { transform: StockscaleTransformer } ]}
        data={parsedData}
        type="hybrid"
      >
        <Chart id={1} xAccessor={ d => d.date }
               yMousePointerDisplayLocation="right"
               yMousePointerDisplayFormat={d3.format(".0%")}
        >
          <XAxis axisAt="bottom" orient="bottom"/>
          <YAxis axisAt="right" orient="right" ticks={5} tickFormat={d3.format(".0%")}/>
          <DataSeries id={0} yAccessor={d => d.fee }>
            <LineSeries stroke="#FF2D04" />
          </DataSeries>
        </Chart>
        <Chart id={2} xAccessor={ d => d.date }
               yMousePointerDisplayLocation="left"
               yMousePointerDisplayFormat={d3.format(",")}
        >
          <YAxis axisAt="left" orient="left" ticks={5}/>
          <DataSeries id={0} yAccessor={d => d.available }>
            <HistogramSeries />
          </DataSeries>
        </Chart>
        <MouseCoordinates xDisplayFormat={d3.time.format("%Y-%m-%d")} type="crosshair" />
        <EventCapture mouseMove={true} mainChart={1}/>
        <TooltipContainer>
          <SingleValueTooltip
            forChart={1}
            forSeries={0}
            yLabel="Fee"
            origin={[-80, -40]}
            yDisplayFormat={d3.format(".0%")}
            fontSize={16}
            xLabel="Date"
            xDisplayFormat={d3.time.format("%Y-%m-%d")}
            labelStroke="#2C3E50"
          />
          <SingleValueTooltip
            forChart={2}
            forSeries={0}
            yLabel="Available"
            xLabel="Date"
            xDisplayFormat={d3.time.format("%Y-%m-%d")}
            origin={[-80, -20]}
            yDisplayFormat={d3.format(",")}
            fontSize={16}
            labelStroke="#2C3E50"
          />
        </TooltipContainer>

      </ChartCanvas>
    );
  }
}

export default fitWidth(StockChart);