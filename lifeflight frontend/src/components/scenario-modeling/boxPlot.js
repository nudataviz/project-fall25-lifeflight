import * as Plot from "npm:@observablehq/plot";

export const boxPlot = (data, showOutlier) => {

  return Plot.plot({
    marginLeft: 60,
    y: {
      grid: true,
      label: "↑ Mileage (miles)"
    },
    fx: {
      label: "Vehicle →",
      labelAnchor: "right"
    },
    marks: [
      Plot.ruleY([0]),
      Plot.boxY(data, {
        fx: "veh", 
        y: "mileage",
        r: showOutlier ? 3 : 0,
      }),
  ],
  })
}