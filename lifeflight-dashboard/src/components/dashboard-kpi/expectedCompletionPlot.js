import * as Plot from "npm:@observablehq/plot";

export function expectedCompletionPlot(data) {
  // 处理数据，计算每个基地的完成比例
  const processedData = data.map(d => ({
    appropriateAsset: d.appropriateAsset,
    total: d.total_count,
    completed: d.completed_count,
    completionRate: d.total_count > 0 ? d.completed_count / d.total_count : 0
  }));
  
  return Plot.plot({
    title: "Expected Completion Rate by Base (2024)",
    axis: null,
    label: null,
    height: 200,
    marginTop: 20,
    marginBottom: 70,
    fx: {
      label: "Expected Base"
    },
    marks: [
      Plot.axisFx({lineWidth: 10, anchor: "bottom", dy: 20}),
      // 总任务数（背景）
      Plot.waffleY(processedData, {
        fx: "appropriateAsset", 
        y: "total", 
        fillOpacity: 0.4, 
        rx: "100%"
      }),
      // 按预期完成的数量（前景）
      Plot.waffleY(processedData, {
        fx: "appropriateAsset", 
        y: "completed", 
        rx: "100%", 
        fill: "orange"
      }),
      // 显示完成比例
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

