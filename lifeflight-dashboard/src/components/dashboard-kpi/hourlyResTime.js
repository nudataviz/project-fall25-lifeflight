import * as Plot from "npm:@observablehq/plot";
import * as d3 from "npm:d3";

export function hourlyResTime(data) {
  return Plot.plot({
    title: "Response Time by Hour of Day",
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
      label: "Response Time (minutes)",
      nice: true
    },
    marks: [
      Plot.ruleY([0]),
      // 标准差区间（阴影区域）
      // Plot.areaY(data, {
      //   x: "Hour",
      //   y1: "lower",
      //   y2: "upper",
      //   fill: "#FF5733",
      //   fillOpacity: 0.2,
      //   stroke: "#FF5733",
      //   strokeWidth: 0.5,
      //   curve: "cardinal"
      // }),
      // 平均值线
      Plot.lineY(data, {
        x: "Hour",
        y: "response_time",
        stroke: "#2E86C1",
        strokeWidth: 2,
        curve: "cardinal",
        // tension: 'basis',
        tip: 'xy'
      }),
      // 平均值点
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