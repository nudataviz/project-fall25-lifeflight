import * as Plot from "../../../_npm/@observablehq/plot@0.6.17/d761ef9b.js";
import * as d3 from "../../../_npm/d3@7.9.0/e780feca.js";

export function hourlyResTime(data) {
  return Plot.plot({
    title: "Dispatch Response Time by Hour of Day(enrtime - disptime) - 2024.08",
    width: 1000,
    height: 500,
    marginTop: 40,
    marginBottom: 50,
    marginLeft: 60,
    x: {
      label: "Hour of Day",
      type: "band",
      domain: d3.range(24)
    },
    r: {range: [0, 14]},
    y: {
      grid: true,
      label: "Dispatch Response Time (minutes)",
      nice: true
    },
    marks: [
      Plot.ruleY([0]),
      Plot.lineY(data, {
        x: "Hour",
        y: "response_time",
        stroke: "#2E86C1",
        strokeWidth: 2,
        curve: "cardinal",
        // tension: 'basis',
        tip: 'xy'
      }),
      Plot.dot(data, {
        x: "Hour",
        y: "response_time",
        fill: "#2E86C1",
        r: 4,
        stroke: "white",
        strokeWidth: 1,
        tip: true
      })
    ]
  });
}