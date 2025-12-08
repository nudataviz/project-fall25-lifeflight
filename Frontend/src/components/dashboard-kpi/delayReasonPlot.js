import * as Plot from "npm:@observablehq/plot";


export function delayReasonPlot(data) {
  
  const processedData = data.filter(d => {
    const reason = d.reason;
    return reason !== 'noDelays' && 
            reason !== null && 
            reason !== undefined &&
            reason !== "0" &&
            reason !== "";
  });
  return Plot.plot({
    title: "Delay Reason - 2024.08",
    marginLeft: 200,
    height: 400,
    x: {
      axis: "top",
      grid: true,
    },
    marks: [
      Plot.ruleX([0]),
      Plot.barX(processedData, {x: "count", y: "reason", sort: {y: "x", reverse: true}, fill: "#87CEEB"})
    ]
  })
}