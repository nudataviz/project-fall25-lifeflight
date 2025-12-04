import * as Plot from "npm:@observablehq/plot";

export function noResponseReasonPlot(data) {

  // 过滤空值和无效数据
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
      title: "No Response Reasons by Base (2024)",
      width: 400,
      height: 200,
      marginLeft: 200,
      marginRight: 20,
      marks: [
        Plot.text(["No valid data available"], {frameAnchor: "middle", fontSize: 16})
      ]
    });
  }
  
  // 按基地分组计算百分比
  const baseGroups = {};
  processedData.forEach(d => {
    const base = d.base;
    if (!baseGroups[base]) {
      baseGroups[base] = [];
    }
    baseGroups[base].push(d);
  });
  
  // 计算每个基地的总数，然后计算百分比
  Object.keys(baseGroups).forEach(base => {
    const total = baseGroups[base].reduce((sum, d) => sum + d.count, 0);
    baseGroups[base].forEach(d => {
      d.percentage = d.count / total;
      d.total = total;
    });
  });
  
  // 展平数据
  const flatData = Object.values(baseGroups).flat();
  
  // 按总数排序原因（显示最常见的原因）
  const reasonTotals = {};
  flatData.forEach(d => {
    if (!reasonTotals[d.reason]) {
      reasonTotals[d.reason] = 0;
    }
    reasonTotals[d.reason] += d.count;
  });
  
  // 获取所有唯一的原因和基地
  const allReasons = [...new Set(flatData.map(d => d.reason))].sort((a, b) => 
    (reasonTotals[b] || 0) - (reasonTotals[a] || 0)
  );
  const allBases = [...new Set(flatData.map(d => d.base))].sort();
  
  // 创建完整的热力图数据（包括0值）
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
  
  // 计算颜色范围
  const maxPercentage = Math.max(...heatmapData.map(d => d.percentage));
  
  // 根据基地数量动态计算宽度，避免右边空白
  const baseCount = allBases.length;
  // 每个基地约75px（包括单元格和间距），加上左边距200px和右边距20px
  const calculatedWidth = Math.max(400, baseCount * 75 + 200 + 20);
  
  return Plot.plot({
    title: "No Response Reasons by Base (2024)",
    width: calculatedWidth,
    height: Math.max(400, allReasons.length * 25),
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
      // 在单元格中显示百分比文本（如果百分比大于5%）
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

