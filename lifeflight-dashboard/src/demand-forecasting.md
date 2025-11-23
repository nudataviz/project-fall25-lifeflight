---
title: Demand Forecasting
---

# 1.1 Prophet Model Prediction

Advanced Prophet model with customizable parameters and extra regressors

This model allows you to add extra regressors (like population demographics) and customize model parameters. The forecast includes historical fit and confidence intervals.

```js
const periods = Inputs.range([1, 10], {
  label: "Predict years",
  value: 1,
  step: 1,
  // format: (x) => `${x}`,
})

const seasonalityMode = Inputs.select(
  ["additive", "multiplicative"],
  {
    label: "Seasonality Mode",
    value: "additive",
    format: (x) => x === "additive" ? "Additive Mode" : "Multiplicative Mode"
  }
)

const growth = Inputs.select(
  ["linear", "logistic"],
  {
    label: "Growth Mode",
    value: "linear",
    format: (x) => x === "linear" ? "Linear Growth" : "Logistic Growth"
  }
);


const yearlySeasonality = Inputs.checkbox({
  label: "Yearly Seasonality",
  value: true
});

const weeklySeasonality = Inputs.checkbox({
  label: "Weekly Seasonality",
  value: false
});

const dailySeasonality = Inputs.checkbox({
  label: "Daily Seasonality",
  value: false
});

const changepointPriorScale = Inputs.range([0.001, 0.5], {
  label: "Changepoint Prior Scale",
  value: 0.05,
  step: 0.001,
  format: (x) => x.toFixed(3)
});

const seasonalityPriorScale = Inputs.range([0.1, 50], {
  label: "Seasonality Prior Scale",
  value: 10.0,
  step: 0.1,
  format: (x) => x.toFixed(1)
});

const intervalWidth = Inputs.range([0.5, 0.99], {
  label: "Confidence Interval Width",
  value: 0.95,
  step: 0.01,
  // format: (x) => `${(x * 100).toFixed(0)}%`
});
```


```js
const availableRegressors = [
  "population",
  "age_0_17",
  "age_18_64", 
  "age_65_plus",
  "precipitation"
];

const extraVars = Inputs.select(availableRegressors, {
  label: "Extra Regressors",
  multiple: true,
  value: []
});
```


```js
periods
```

${growth}

${seasonalityMode}

<div class="card" style="padding: 1.5rem;">
  <h2 style="margin-top: 0;">Model Parameters Configuration</h2>
  
  <div class="grid grid-cols-2" style="gap: 1rem; margin-bottom: 1rem;">
    <div>
      <!-- <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;"></label> -->
      ${periods}
    </div>
    <div>
      <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;"></label>
      ${growth}
    </div>
  </div>
  
  <div style="margin-bottom: 1rem;">
    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">${seasonalityMode.label}</label>
    ${seasonalityMode}
  </div>
  
  <div style="margin-bottom: 1rem;">
    <h3 style="font-size: 1rem; margin-bottom: 0.5rem;">Seasonality Options</h3>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
      <div>${yearlySeasonality}</div>
      <div>${weeklySeasonality}</div>
      <div>${dailySeasonality}</div>
    </div>
  </div>
  
  <div style="margin-bottom: 1rem;">
    <h3 style="font-size: 1rem; margin-bottom: 0.5rem;">Advanced Parameters</h3>
    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
      ${changepointPriorScale}
      ${seasonalityPriorScale}
      ${intervalWidth}
    </div>
  </div>
  
  <div>
    <h3 style="font-size: 1rem; margin-bottom: 0.5rem;">Extra Regressors</h3>
    ${extraVars}
  </div>
</div>

```js
typeof growth
```


```js
const modelParams = {
  periods: Number(periods) || 12,
  // growth: String(growth || 'linear'),
  yearly_seasonality: Boolean(yearlySeasonality),
  weekly_seasonality: Boolean(weeklySeasonality),
  daily_seasonality: Boolean(dailySeasonality),
  // seasonality_mode: String(seasonalityMode || 'additive'),
  changepoint_prior_scale: Number(changepointPriorScale) || 0.05,
  seasonality_prior_scale: Number(seasonalityPriorScale) || 10.0,
  interval_width: Number(intervalWidth) || 0.95,
  extra_vars: Array.isArray(extraVars) ? extraVars : []
};

let forecastData = null;
let error = null;


const response = await fetch("http://localhost:5001/api/predict_demand_v2", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(modelParams)
});
forecastData = await response.json();
  
```


```js
forecastData
```

