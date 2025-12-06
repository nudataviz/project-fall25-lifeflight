import * as Plot from "../../../_npm/@observablehq/plot@0.6.17/d761ef9b.js";

export function expectedCompletionPlot(data) {
  let processedData = null;
  processedData = data.map(d => ({
    appropriateAsset: d.appropriateAsset,
    total: d.total_count,
    completed: d.completed_count,
    completionRate: d.total_count > 0 ? d.completed_count / d.total_count : 0
  }));
  processedData = processedData.filter(d => d.appropriateAsset !== 'dhart');
  
  const baseCount = processedData.length;

  const calculatedWidth = Math.max(400, baseCount * 65 + 40);
  
  return Plot.plot({
    title: "Expected Completion Rate by Base - 2024.08",
    axis: null,
    label: null,
    width: calculatedWidth,
    marginTop: 20,
    marginBottom: 70,
    marginRight: 20,
    fx: {
      label: "Expected Base"
    },
    marks: [
      Plot.axisFx({lineWidth: 10, anchor: "bottom", dy: 20}),
      Plot.waffleY(processedData, {
        fx: "appropriateAsset", 
        y: "total", 
        fillOpacity: 0.4, 
        rx: "100%"
      }),
      Plot.waffleY(processedData, {
        fx: "appropriateAsset", 
        y: "completed", 
        rx: "100%", 
        fill: "orange"
      }),
      Plot.text(processedData, {
        fx: "appropriateAsset", 
        text: (d) => (d.completionRate).toLocaleString("en-US", {style: "percent"}), 
        frameAnchor: "bottom", 
        lineAnchor: "top", 
        dy: 6, 
        fill: "orange", 
        fontSize: 24,
        fontWeight: "bold"
      })
    ]
  })
}

