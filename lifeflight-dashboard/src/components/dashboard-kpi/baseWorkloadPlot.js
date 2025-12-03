import * as Plot from "npm:@observablehq/plot";

export function baseWorkloadPlot(data) {
  
  const processedData = Object.entries(data).map(([base, count]) => ({
    base: base,
    count: count,
    type: ['LF1','LF2','LF3','LF4'].includes(base) ? 'airUnit' : 'groundUnit',
  }));

  
  return Plot.plot({
    title: "Base Workload",
    width: 600,
    height: 300,
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
      range: ["#2E86C1", "#E74C3C"],
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