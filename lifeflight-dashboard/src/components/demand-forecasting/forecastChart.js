import * as Plot from "npm:@observablehq/plot";

export function forecastChart(data) {
  const { ciData, actualData, predictedData, lastActualDate } = data;
  
  return Plot.plot({
    // title: "Demand Forecast",
    subtitle: "Actual vs Predicted with Confidence Intervals",
    width: 1200,
    height: 700,
    marginTop: 50,
    marginBottom: 50,
    x: {
      type: "time",
      label: "Date",
      tickRotate: -45,
      // tickValues: yearTicks,
      // ticks: 10,
    },
    y: {
      grid: true,
      label: "Task Count"
    },
    color: {
      domain: ["Actual", "Predicted"],
      range: ["#2E86C1", "#28B463"]
    },
    marks: [
      Plot.areaY(ciData, {
        x: "date",
        y1: "lower",
        y2: "upper",
        fill: "#FF5733",
        fillOpacity: 0.2,
        stroke: "#FF5733",
        strokeWidth: 0.5,
        curve: "catmull-rom"
      }),
      // actual data
      Plot.lineY(actualData, {
        x: "date",
        y: "value",
        stroke: "#2E86C1",
        strokeWidth: 2,
        tip: true
      }),
      // predict
      Plot.lineY(predictedData, {
        x: "date",
        y: "value",
        stroke: "green",
        strokeWidth: 2,
        strokeDasharray: "4,2",
        tip: true
      }),
      // historical data separator line
      lastActualDate ? Plot.ruleX([lastActualDate], {
        stroke: "#95A5A6",
        strokeWidth: 2,
        strokeDasharray: "5,5",
        opacity: 0.8
      }) : null,
      Plot.ruleY([0], {
        stroke: "#95A5A6",
        strokeWidth: 1,
        opacity: 0.5
      }),
      Plot.dot(actualData, {
        x: "date",
        y: "value",
        fill: "#2E86C1",
        r: 3,
        tip: true
      }),
      Plot.dot(predictedData, {
        x: "date",
        y: "value",
        fill: "#28B463",
        r: 3,
        tip: true
      })
    ].filter(Boolean), 
    legend: {
      color: {
        title: "Data Type",
        label: null
      }
    }
  });
}