import * as Plot from "npm:@observablehq/plot";


export function delayReasonPlot(data) {
  return Plot.plot({
    title: "Delay Reason",
    marginLeft: 200,
    height: 400,
    x: {
      axis: "top",
      grid: true,
      percent: true
    },
    marks: [
      Plot.ruleX([0]),
      Plot.barX(data, {x: "count", y: "reason", sort: {y: "x", reverse: true}})
    ]
  })
}