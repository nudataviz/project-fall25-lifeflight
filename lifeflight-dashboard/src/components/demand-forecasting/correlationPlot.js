import * as Plot from "npm:@observablehq/plot";

export function correlationPlot(correlationData) {
  
  const data = Object.entries(correlationData).map(([variable, value]) => ({
    variable: variable,
    correlation: value
  }));
  

  const positive = data.filter(d => d.correlation >= 0).sort((a, b) => b.correlation - a.correlation);
  const negative = data.filter(d => d.correlation < 0).sort((a, b) => a.correlation - b.correlation);
  
  const sortedData = [...positive, ...negative];
  
  const maxAbs = Math.max(...sortedData.map(d => Math.abs(d.correlation)));
  const yDomain = [-Math.max(maxAbs, 1), Math.max(maxAbs, 1)];
  
  const formatVariableName = (name) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace(/Ratio/g, ' Ratio')
      .replace(/Population/g, ' Population');
  };
  
  sortedData.forEach(d => {
    d.formattedVariable = formatVariableName(d.variable);
  });
  
  return Plot.plot({
    title: "Correlation with Mission Count",
    height: 300,
    width: 500,
    marginTop: 50,
    marginLeft: 70,
    marginBottom: 70,
    x: {
      label: "Variable",
      type: "band",
      domain: sortedData.map(d => d.formattedVariable),
      tickRotate: -15
    },
    y: {
      label: "Correlation",
      domain: yDomain,
      grid: true,
      tickFormat: (d) => d.toFixed(2),
      line: true
    },
    marks: [
      // 0线
      Plot.ruleY([0], {
        stroke: "#000",
        strokeWidth: 2,
        strokeDasharray: "4,2"
      }),
      // 条形图 - 正相关用蓝色，负相关用红色
      Plot.barY(sortedData, {
        x: "formattedVariable",
        y: "correlation",
        fill: d => d.correlation >= 0 ? "#2E86C1" : "#E74C3C",
        tip: {
          format: {
            variable: true,
            correlation: (d) => d.correlation.toFixed(4)
          }
        }
      }),
      // 在条形图上显示数值
      // Plot.text(sortedData, {
      //   x: "formattedVariable",
      //   y: "correlation",
      //   text: (d) => d.correlation.toFixed(2),
      //   textAnchor: "middle",
      //   dy: d => d.correlation >= 0 ? -8 : 8,
      //   fill: "black",
      //   fontSize: 11,
      //   fontWeight: "bold"
      // })
    ]
  })
}

