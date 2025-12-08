export function prepareChartData(forecastData) {
  if (!forecastData || !forecastData.data) return null;
  
  const { forecast_data, historical_actual } = forecastData.data;
  
  const ciData = forecast_data.map(d => ({
    date: d.date,
    upper: d.upper,
    lower: d.lower
  }));
  
  const actualData = historical_actual.map(d => ({
    date: d.date,
    value: d.actual,
    type: "Actual"
  }));
  
  const predictedData = forecast_data.map(d => ({
    date: d.date,
    value: d.predicted,
    type: "Predicted"
  }));
  
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