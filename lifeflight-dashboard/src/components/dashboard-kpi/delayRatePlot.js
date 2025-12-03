import * as Plot from "npm:@observablehq/plot";

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
    title: "Delay Rate(2024)",
    axis: null,
    label: null,
    height: 200,
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