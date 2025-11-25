---
title: Demand Forecasting
---

# 1 Demand Forecasting

<br/>

## 1.1 Prophet Model Prediction

Using the Prophet model, we forecast LifeFlight’s future demand based on historical data from 2013–2023. The target is the total number of missions per month. Prophet captures long-term trends and seasonal patterns, and it also supports extra regressors to enhance forecasting performance.

You can adjust the model parameters below.

### Input parameters


<div class='card'>
<h4>Basic parameters<h4/>
<div>

```js
const periods = view(Inputs.range([1, 10], {
  label: "Predict years",
  value: 1,
  step: 1,
}))

const seasonalityMode = view(Inputs.select(
  ["additive", "multiplicative"],
  {
    label: "Seasonality Mode",
    value: "additive",
    format: (x) => x === "additive" ? "Additive Mode" : "Multiplicative Mode"
  }
))

const growth = view(Inputs.select(
  ["linear", "logistic"],
  {
    label: "Growth Mode",
    value: "linear",
    format: (x) => x === "linear" ? "Linear Growth" : "Logistic Growth"
  }
))

const yearlySeasonality = view(Inputs.toggle(
  {
    label: "Yearly Seasonality",
    value: true,
   }
  ))


const changepointPriorScale = view(Inputs.range([0.001, 0.5], {
  label: "Changepoint Prior Scale",
  value: 0.05,
  step: 0.001,
  format: (x) => x.toFixed(3)
}))

const seasonalityPriorScale = view(Inputs.range([0.1, 50], {
  label: "Seasonality Prior Scale",
  value: 10.0,
  step: 0.1,
  format: (x) => x.toFixed(1)
}))

const intervalWidth = view(Inputs.range([0.5, 0.99], {
  label: "Confidence Interval Width",
  value: 0.95,
  step: 0.01,
}))
```
</div>
</div>

<div class='card'>
<h4>Extra variables parameters<h4/>
<div>

```js
const availableRegressors = [
  'age_under_5_ratio',
  'age_5_9_ratio',
  'age_10_19_ratio',
  'age_20_29_ratio',
  'age_30_39_ratio',
  'age_40_49_ratio',
  'age_50_59_ratio',
  'age_60_69_ratio',
  'age_70_79_ratio',
  'age_80_84_ratio',
  'age_85_plus_ratio',
  'total_population'
];

const extraVars = view(Inputs.checkbox(availableRegressors, {
  label: "Extra Regressors",
  multiple: true,
  value: []
}))

const regressorMode = view(Inputs.radio(['additive','multiplicative'],
{
  label: "Regressor Mode",
  value: "additive"
}
))

const regressorPriorScale = view(Inputs.range([0.001, 0.5], {
  label: "Regressor Prior Scale",
  value: 0.05,
  step: 0.001,
  format: (x) => x.toFixed(3)
}))
```
</div>
</div>



```js
const modelParams = {
  periods: periods*12,
  growth,
  seasonality_mode: seasonalityMode,
  yearly_seasonality: yearlySeasonality,
  changepoint_prior_scale: changepointPriorScale,
  seasonality_prior_scale: seasonalityPriorScale,
  interval_width: intervalWidth,
  extra_vars: extraVars || [],
  regressor_prior_scale: regressorPriorScale || null,
  regressor_mode: regressorMode || null,
};

let forecastData = null;
let error = null;

try{
  const response = await fetch('http://localhost:5001/api/predict_demand_v2', {
    method: 'POST',
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(modelParams)
  })
  if(!response.ok){
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  forecastData = await response.json()
  error = null
} catch (e) {
  error = e.message
  forecastData = null
  console.error('fetch error:', e)
}
  
```


```js 
import {prepareChartData} from "./components/demand-forecasting/prepareLineChartData.js"
```

```js
const chartData = forecastData?.data ? prepareChartData(forecastData) : null;
```

```js
import {forecastChart} from "./components/demand-forecasting/forecastChart.js"
import {calculateMetrics} from "./components/demand-forecasting/metrics.js"
```

### Predict Chart

```js
if(error){
  html`<div style="color: red;">Error: ${error}</div>`
}
```
```js
forecastChart(chartData)
```

### Model Performance Metrics
```js
calculateMetrics(forecastData.data.cv_metrics)
```


## 1.2 Day-of-Week/Hour Heatmap

This chart aggregates historical operational data by weekday and hour to reveal cyclical patterns in LifeFlight demand. Color intensity represents the number of missions in each hour, highlighting differences between weekdays and weekends and variations across times of day.

Please select the year and month you’d like to view.

```js
const heatmapYear = view(Inputs.range([2013,2023],{
  label:'Select Year',
  step:1,
  value:2013,
  }
))

const heatmapMonth = view(Inputs.radio(
    new Map([
      ["JAN", 1],
      ["FEB", 2],
      ["MAR", 3],
      ["APR", 4],
      ["MAY", 5],
      ["JUN", 6],
      ["JUL", 7],
      ["AUG", 8],
      ["SEP", 9],
      ["OCT", 10],
      ["NOV", 11],
      ["DEC", 12],
    ]),
    {value: 1, label: "Select Month", format: ([name, value]) => `${name}`}
  ))
```


```js
// fetch 1.2
const heatmapParams = new URLSearchParams({
  year: heatmapYear.toString(),
  month: heatmapMonth.toString(),
})
const heatMapResponse = await fetch(`http://localhost:5001/api/seasonality_heatmap?${heatmapParams}`)
if (!heatMapResponse.ok) {
    const errorData = await heatMapResponse.json();
    throw new Error(errorData.message || `HTTP error! status: ${heatMapResponse.status}`);
  }
```

```js
const heatmapData= await heatMapResponse.json()
```


```js
import {demandHeatmap} from "./components/demand-forecasting/demandHeatmap.js"
```

```js

demandHeatmap(heatmapData.data,heatmapYear,heatmapMonth)
```