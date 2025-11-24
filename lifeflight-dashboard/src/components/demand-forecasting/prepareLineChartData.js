// 准备图表数据
export function prepareChartData(forecastData) {
  if (!forecastData || !forecastData.data) return null;
  
  const { forecast_data, historical_actual } = forecastData.data;
  
  // 准备置信区间数据（用于 area）
  const ciData = forecast_data.map(d => ({
    date: d.date,
    upper: d.upper,
    lower: d.lower
  }));
  
  // 准备历史实际数据
  const actualData = historical_actual.map(d => ({
    date: d.date,
    value: d.actual,
    type: "Actual"
  }));
  
  // 准备预测数据
  const predictedData = forecast_data.map(d => ({
    date: d.date,
    value: d.predicted,
    type: "Predicted"
  }));
  
  // 找到历史数据的最后日期（用于画分隔线）
  const lastActualDate = historical_actual.length > 0 
    ? historical_actual[historical_actual.length - 1].date 
    : null;
  
  return {
    ciData,
    actualData,
    predictedData,
    allData: [...actualData, ...predictedData],
    lastActualDate
  };
}