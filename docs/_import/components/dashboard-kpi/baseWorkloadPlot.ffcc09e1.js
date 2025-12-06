import * as Plot from "../../../_npm/@observablehq/plot@0.6.17/d761ef9b.js";

export function baseWorkloadPlot(data) {
  
  const processedData = Object.entries(data).map(([base, count]) => ({
    base: base,
    count: count,
    type: ['LF1','LF2','LF3','LF4'].includes(base) ? 'airUnit' : 'groundUnit',
  }));

  
  return Plot.plot({
    title: "Base Workload - 2024.08",
    width: 1000,
    height: 500,
    marginLeft: 80,
    x: {
      label: "Mission Count",
      grid: true
    },
    y: {
      label: "Base",
      type: "band"
    },
    color: {
      domain: ["airUnit", "groundUnit"],
      range: ["#87CEEB", "#1E3A8A"],
      legend: true,
    },
    marks: [
      Plot.ruleX([0]),
      Plot.barX(processedData, {
        y: "base",
        x: "count",
        fill: "type",
        sort: { y: "x", reverse: true }
      }),
      Plot.text(processedData, {
        y: "base",
        x: "count",
        text: d => `${d.count}`,
        textAnchor: "start",
        dx: 4,
        fill: "currentColor"
      })
    ]
  });
}