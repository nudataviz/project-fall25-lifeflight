import * as Plot from "../../../_npm/@observablehq/plot@0.6.17/d761ef9b.js";

export function delayPlot(data) {
  const grouped = {};
  
  data.forEach(d => {
    const asset = d.respondingAssets;
    if (!grouped[asset]) {
      grouped[asset] = {
        respondingAssets: asset,
        yes: 0,
        total: 0
      };
    }
    
    grouped[asset].total += d.count || 0;
    
    if (d.transportByPrimaryQ === 'yes') {
      grouped[asset].yes += d.count || 0;
    }
  });
  
  const processedData = Object.values(grouped);
  
  return Plot.plot({
    title: "Transport by Appropriate Asset Without Delay - 2024.08",
    axis: null,
    label: null,
    height: 400,
    marginTop: 20,
    marginBottom: 70,
    fx: {
      label: "Responding Assets"
    },
    marks: [
      Plot.axisFx({lineWidth: 10, anchor: "bottom", dy: 20}),
      Plot.waffleY(processedData, {
        fx: "respondingAssets", 
        y: "total", 
        fillOpacity: 0.4, 
        rx: "100%"
      }),
      Plot.waffleY(processedData, {
        fx: "respondingAssets", 
        y: "yes", 
        rx: "100%", 
        fill: "orange"
      }),
      Plot.text(processedData, {
        fx: "respondingAssets", 
        text: (d) => (d.yes / d.total).toLocaleString("en-US", {style: "percent"}), 
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