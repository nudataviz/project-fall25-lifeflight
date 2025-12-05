---
toc: false
theme: dashboard
---

```js
let indicatorData = null;
let error = null;
try{
  const response = await fetch('http://localhost:5001/api/indicators')
  if(!response.ok){
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  indicatorData = await response.json()
}catch(e){
  error = e.message
  console.error('Error', error)
}
```
<div class="hero">
  <h1>Lifeflight Dashboard</h1>
  <h2>Welcome to Lifeflight Dashboard!</h2>
  <a href="https://lifeflightmaine.org/">LifeFlight Website<span style="display: inline-block; margin-left: 0.25rem;">↗︎</span></a>
</div>

Last data date: 2024.08
<!-- indicator card -->
<div class="grid grid-cols-2">
  <div class="card">
    <h2>📈 Total Missions Completed(2024.08)</h2>
    <span class="big">${indicatorData?.data?.total_missions}</span>
  </div>
  <div class="card">
    <h2>📍 Cities Served</h2>
    <span class="big">${indicatorData?.data?.total_cities_covered}</span>
  </div>
  <!-- <div class="card">
    <h2>⏱️ Response Time <span class="muted"> Monthly average</span></h2>
    <span class="big">${indicatorData?.data?.mart}</span>
  </div> -->
</div>

# <span style="white-space: nowrap;">Dispatch Time and Mission Volume: 24-Hour Distribution for This Month</span>

```js
const responseDis = await fetch('http://localhost:5001/api/get_24hour_distribution')
const dataDis = await responseDis.json()
```
```js
import {missionDisPlot} from './components/dashboard-kpi/missionDisPlot.js'
```
```js
const distributionMode = view(Inputs.select(
  ["hourly", "weekday"],
  {
    label: "Distribution Type",
    value: "hourly",
    format: (x) => x === "hourly" ? "24-Hour Distribution" : "Weekly Distribution"
  }
))
```
```js
const missionData = distributionMode === "hourly" 
  ? dataDis.data.hourly_distribution 
  : dataDis.data.weekday_distribution;
```
```js
missionDisPlot(missionData, distributionMode)
```


```js
import {hourlyResTime} from './components/dashboard-kpi/hourlyResTime.js'
```

```js
hourlyResTime(dataDis.data.response_time)
```

# Base Workload

<!-- Count of airUnit and groundUnit when "Did LFOM transport patient" is yes -->

```js
const resBaseCount = await fetch('http://localhost:5001/api/get_mission_count_for_each_base')
const dataBase = await resBaseCount.json()
```

```js
import {baseWorkloadPlot} from './components/dashboard-kpi/baseWorkloadPlot.js'
```

```js
baseWorkloadPlot(dataBase.data)
```



# Transport by Appropriate Asset Without Delay

Uses the "Transport by Primary Q" field. A task is marked as "Yes" when both conditions are met: (1) using the expected/appropriate asset, and (2) no delay. Otherwise, it is marked as "No".

Delay Rate (2024.08) shows the proportion of tasks completed with "Transport by Primary Q" by each base in 2024.08, evaluating overall performance in completing tasks on time with the expected asset. Delay Reason analyzes the main causes of delays for tasks with delays, identifying time-related bottlenecks.

The analysis of expected completion rates and non-response reasons focuses on whether the most appropriate asset was used, evaluating asset matching and dispatch decision performance, and analyzing main reasons for not responding with the expected asset.


```js
let resTest=null
let data = null
resTest = await fetch('http://localhost:5001/api/test')
data = await resTest.json()
```


```js
import {delayPlot} from './components/dashboard-kpi/delayRatePlot.js'
import {delayReasonPlot} from './components/dashboard-kpi/delayReasonPlot.js'
import {expectedCompletionPlot} from './components/dashboard-kpi/expectedCompletionPlot.js'
```


<div style='display: flex;align-items: center;'>
<div class='card'>
${delayPlot(data.delayData)}
</div>
<div class='card'>
${delayReasonPlot(data.delayReasonData)}
</div>

</div>

# Expected Completion Rate and Non-Response Reasons by Base

This section evaluates base dispatch performance based on whether the most appropriate base executed each task, comparing expected vs. actual execution. The field "appropriateAsset" (Who should have gone if available) indicates the base initially assigned and expected to execute the task; the field "respondingAssets" records the base that actually executed the task.

The chart "Expected Completion Rate by Base (2024.08)" shows the proportion of expected tasks actually completed by the expected base in 2024.08, measuring each base's ability to execute tasks as planned. It also shows the proportion of non-response reasons for LF1-LF4, analyzing factors such as resource occupancy, maintenance, and distance limitations that affect bases' ability to execute tasks as expected.
```js
import {noResponseReasonPlot} from './components/dashboard-kpi/noResponseReasonPlot.js'
```

<div style='display: flex;align-items: center;'>
<div class='card'>
${expectedCompletionPlot(data.expectedCompletionData)}
</div>
<div class='card'>
${noResponseReasonPlot(data.noResponseReasonsData)}
</div>
</div>

<!-- # 热力图

```js
let mapHtml = null
let error = null
try{
  const mapResponse = await fetch('HTTP://localhost:5001/api/heatmap')
  if(!mapResponse.ok){
    throw new Error(`HTTP ${mapResponse.status}: ${mapResponse.statusText}`)
  }
  mapHtml = await mapResponse.text()
}catch(e){
  error = e.message
  console.log('Error',error)
}

```


```js
  html`
    <div class="card" style="overflow: hidden;">
    <h2>LifeFlight Pickup Location Heatmap</h2>
    <h3 style="color: #666;white-space: nowrap">
      Heatmap of all patient transports from July 2012 to December 2023, based on pickup city locations.</h3>
      <iframe 
        srcdoc=${mapHtml}
        style="width: 100%; height: 500px; border: none;"
        title="Heatmap"
      ></iframe>
    </div>
  `
```
 -->



<!--  
<div class="grid grid-cols-2" style="grid-auto-rows: 504px;">
  <div class="card">${
    resize((width) => Plot.plot({
      title: "Your awesomeness over time 🚀",
      subtitle: "Up and to the right!",
      width,
      y: {grid: true, label: "Awesomeness"},
      marks: [
        Plot.ruleY([0]),
        Plot.lineY(aapl, {x: "Date", y: "Close", tip: true})
      ]
    }))
  }</div>
  <div class="card">${
    resize((width) => Plot.plot({
      title: "How big are penguins, anyway? 🐧",
      width,
      grid: true,
      x: {label: "Body mass (g)"},
      y: {label: "Flipper length (mm)"},
      color: {legend: true},
      marks: [
        Plot.linearRegressionY(penguins, {x: "body_mass_g", y: "flipper_length_mm", stroke: "species"}),
        Plot.dot(penguins, {x: "body_mass_g", y: "flipper_length_mm", stroke: "species", tip: true})
      ]
    }))
  }</div>
</div>

---

## Next steps

Here are some ideas of things you could try…

<div class="grid grid-cols-4">
  <div class="card">
    Chart your own data using <a href="https://observablehq.com/framework/lib/plot"><code>Plot</code></a> and <a href="https://observablehq.com/framework/files"><code>FileAttachment</code></a>. Make it responsive using <a href="https://observablehq.com/framework/javascript#resize(render)"><code>resize</code></a>.
  </div>
  <div class="card">
    Create a <a href="https://observablehq.com/framework/project-structure">new page</a> by adding a Markdown file (<code>whatever.md</code>) to the <code>src</code> folder.
  </div>
  <div class="card">
    Add a drop-down menu using <a href="https://observablehq.com/framework/inputs/select"><code>Inputs.select</code></a> and use it to filter the data shown in a chart.
  </div>
  <div class="card">
    Write a <a href="https://observablehq.com/framework/loaders">data loader</a> that queries a local database or API, generating a data snapshot on build.
  </div>
  <div class="card">
    Import a <a href="https://observablehq.com/framework/imports">recommended library</a> from npm, such as <a href="https://observablehq.com/framework/lib/leaflet">Leaflet</a>, <a href="https://observablehq.com/framework/lib/dot">GraphViz</a>, <a href="https://observablehq.com/framework/lib/tex">TeX</a>, or <a href="https://observablehq.com/framework/lib/duckdb">DuckDB</a>.
  </div>
  <div class="card">
    Ask for help, or share your work or ideas, on our <a href="https://github.com/observablehq/framework/discussions">GitHub discussions</a>.
  </div>
  <div class="card">
    Visit <a href="https://github.com/observablehq/framework">Framework on GitHub</a> and give us a star. Or file an issue if you’ve found a bug!
  </div>
</div>
-->
<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 4rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 1rem 0;
  padding: 1rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

</style>
