import * as Plot from "../../../_npm/@observablehq/plot@0.6.17/d761ef9b.js";
import * as d3 from "../../../_npm/d3@7.9.0/e780feca.js";

export function demandHeatmap(heatmapData, year, month) {
  const weekdayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const flatData = [];
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  heatmapData.heatmap_data[0].heatmap.forEach(weekdayData => {
    weekdayData.values.forEach(hourData => {
      flatData.push({
        weekday: weekdayData.weekday,
        weekdayName: weekdayNames[weekdayData.weekday],
        hour: hourData.hour,
        missions_per_1000: hourData.missions_per_1000,
        count: hourData.count
      });
    });
  });

  console.log('flatData',flatData)

  // range of color
  const values = flatData.map(d => d.count)
  const min = Math.min(...values);
  const max = Math.max(...values);

  return Plot.plot({
    title: `Demand Heatmap - ${monthNames[month-1]} ${year}`,
    padding: 0,
    width: 1200,
    height: 500,
    marginTop: 50,
    marginBottom: 50,
    x: {
      type: "band",
      label: "Hour of Day",
      domain: d3.range(24),
    },
    y:{
      type: "band",
      label: "Day of Week",
      domain: weekdayNames,
    },
    color: {
      type: 'linear',
      scheme: 'reds',
      domain: [min,max],
      legend: true,
      label: "Number of Missions",
    },
    marks:[
      Plot.cell(flatData,{
        x: "hour",
        y: "weekdayName",
        fill: "count",
        tip:true,
        inset: 0.5,
      }),
    ]
  })
}