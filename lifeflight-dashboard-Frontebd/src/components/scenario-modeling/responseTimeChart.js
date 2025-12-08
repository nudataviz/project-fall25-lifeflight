import * as Plot from "npm:@observablehq/plot";

export function responseTimeChart(data) {

  const xy = {
    x: "time_diff_minutes",
    y: "PU City",
    z: "PU City"
  };

  return Plot.plot({
    height: 800,
    marginLeft: 100,
    x: {
      axis: "top",
      grid: true,
      label: "Response Time (minutes)"
    },
    y: {
      axis: null,
      label: "Pickup City"
    },
    color: {
      scheme: "spectral",
      legend: true,
      label: "Vehicle Base"
    },
    marks: [
      Plot.ruleX([0]),
      Plot.ruleY(
        data,
        Plot.groupY(
          { x1: "min", x2: "max" },
          { ...xy, sort: { y: "x1" } }
        )
      ),
      Plot.dot(
        data,
        {
          ...xy,
          fill: "TASC Primary Asset ",
          title: (d) => `${d["TASC Primary Asset "]}\n${d.time_diff_minutes?.toFixed(1)} min`,
          sort: { color: null },
          tip: true,
        }
      ),
      Plot.text(
        data,
        Plot.selectMinX({
          ...xy,
          textAnchor: "end",
          dx: -6,
          text: "PU City"
        })
      )
    ]
  });
}

