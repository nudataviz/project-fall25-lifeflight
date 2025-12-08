import * as Plot from "npm:@observablehq/plot";

export function noResponseReasonPlot(data) {

  const processedData = data.filter(d => 
    d && 
    d.reason && 
    d.reason !== '' && 
    d.reason !== null && 
    d.reason !== undefined &&
    d.count > 0
  );
  
  if (processedData.length === 0) {
    return Plot.plot({
      title: "No Response Reasons by Base - 2024.08",
      // width: 400,
      marginRight: 20,
      marks: [
        Plot.text(["No valid data available"], {frameAnchor: "middle", fontSize: 16})
      ]
    });
  }
  
  const baseGroups = {};
  processedData.forEach(d => {
    const base = d.base;
    if (!baseGroups[base]) {
      baseGroups[base] = [];
    }
    baseGroups[base].push(d);
  });
  
  Object.keys(baseGroups).forEach(base => {
    const total = baseGroups[base].reduce((sum, d) => sum + d.count, 0);
    baseGroups[base].forEach(d => {
      d.percentage = d.count / total;
      d.total = total;
    });
  });
  
  const flatData = Object.values(baseGroups).flat();
  
  const reasonTotals = {};
  flatData.forEach(d => {
    if (!reasonTotals[d.reason]) {
      reasonTotals[d.reason] = 0;
    }
    reasonTotals[d.reason] += d.count;
  });
  
  const allReasons = [...new Set(flatData.map(d => d.reason))].sort((a, b) => 
    (reasonTotals[b] || 0) - (reasonTotals[a] || 0)
  );
  const allBases = [...new Set(flatData.map(d => d.base))].sort();
  
  const heatmapData = [];
  allBases.forEach(base => {
    allReasons.forEach(reason => {
      const existing = flatData.find(d => d.base === base && d.reason === reason);
      heatmapData.push({
        base: base,
        reason: reason,
        percentage: existing ? existing.percentage : 0,
        count: existing ? existing.count : 0,
        total: existing ? existing.total : 0
      });
    });
  });
  
  const maxPercentage = Math.max(...heatmapData.map(d => d.percentage));
  
  const baseCount = allBases.length;
  const calculatedWidth = Math.max(400, baseCount * 75 + 200 + 20);
  
  return Plot.plot({
    title: "No Response Reasons by Base - 2024.08",
    width: calculatedWidth,
    height: 400,
    marginLeft: 200,
    marginTop: 40,
    marginBottom: 40,
    marginRight: 20,
    x: {
      type: "band",
      label: "Base",
      domain: allBases
    },
    y: {
      type: "band",
      label: "Reason",
      domain: allReasons
    },
    color: {
      type: "linear",
      scheme: "YlOrRd",
      domain: [0, maxPercentage],
      legend: true,
      label: "Percentage"
    },
    marks: [
      Plot.cell(heatmapData, {
        x: "base",
        y: "reason",
        fill: "percentage",
        tip: {
          format: {
            base: true,
            reason: true,
            percentage: (d) => (d.percentage * 100).toFixed(1) + "%",
            count: (d) => d.count,
            total: (d) => d.total
          }
        },
        inset: 2
      }),
      Plot.text(heatmapData, {
        x: "base",
        y: "reason",
        text: (d) => (d.percentage * 100).toFixed(0) + "%",
        fill: "black",
        fontSize: 11,
        fontWeight: "bold"
      })
    ]
  })
}

