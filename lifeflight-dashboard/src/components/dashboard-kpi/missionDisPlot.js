import * as Plot from "npm:@observablehq/plot";
import * as d3 from "npm:d3";

export function missionDisPlot(data, mode = "hourly") {
  // mode: "hourly" 或 "weekday"
  const marks = [
    Plot.ruleY([0]),
  ];
  
  if (mode === "weekday") {
    // 一周分布：按星期几
    const weekdayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    marks.push(Plot.barY(data, {
      x: "WeekdayName",
      y: "count",
      fill: "#87CEEB"
    }));
    
    return Plot.plot({
      title: "Mission Volume Distribution by Weekday - 2024.08",
      width: 1000,
      height: 500,
      y: {grid: true, label: "Average Missions per Day"},
      x: {
        type: "band",
        domain: weekdayOrder,
        label: "Day of Week"
      },
      marks: marks,
    });
  } else {
    // 24小时分布：按小时
    marks.push(Plot.barY(data, {
      x: "Hour",
      y: "count",
      fill: "#87CEEB"
    }));
    
    return Plot.plot({
      title: "Mission Volume Distribution by Hour of Day - 2024.08",
      width: 1000,
      height: 500,
      y: {grid: true, label: "Mission Count"},
      x: {
        type: "band",
        domain: d3.range(24),
        label: "Hour of Day"
      },
      marks: marks,
    });
  }
}