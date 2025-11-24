---
title: Demand Forecasting
---

# 1 Demand Forecasting

<br/>

## 1.1 Prophet Model Prediction

Advanced Prophet model with customizable parameters and extra regressors

This model allows you to add extra regressors (like population demographics) and customize model parameters. The forecast includes historical fit and confidence intervals.

### Input parameters

<h4>Basic parameters<h4/>

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

<h4>Extra variables parameters<h4/>


```js
const availableRegressors = [
  "population",
  "age_0_17",
  "age_18_64", 
  "age_65_plus",
  "precipitation"
];

const extraVars = view(Inputs.checkbox(availableRegressors, {
  label: "Extra Regressors",
  multiple: true,
  value: []
}))

const regressorMode = view(Inputs.radio(['Additive','Multiplicative'],
{label: "Regressor Mode",
}
))

const regressorPriorScale = view(Inputs.range([0.001, 0.5], {
  label: "Regressor Prior Scale",
  value: 0.05,
  step: 0.001,
  format: (x) => x.toFixed(3)
}))
```




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
```

### Predict Chart

```js
if(error){
  html`<div style="color: red;">Error: ${error}</div>`
}
```
```js
chartData && forecastChart(chartData)
```


## 1.2 Seasonality & Day-of-Week/Hour Heatmap