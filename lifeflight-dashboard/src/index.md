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

Last data date: August 2024; this is the data for August.
<!-- indicator card -->
<div class="grid grid-cols-4">
  <div class="card">
    <h2>📈 Total Missions Completed(2024.08)</h2>
    <span class="big">${indicatorData?.data?.total_missions}</span>
  </div>
  <div class="card">
    <h2>📍 Cities Served</h2>
    <span class="big">${indicatorData?.data?.total_cities_covered}</span>
  </div>
  <div class="card">
    <h2>⏱️ Response Time <span class="muted"> Monthly average</span></h2>
    <span class="big">${indicatorData?.data?.mart}</span>
  </div>
  
  <div class="card">
    <h2>⏱️ Response Time <span class="muted"> Yearly average</span></h2>
    <span class="big">${indicatorData?.data?.yart}</span>
  </div>
</div>

# <span style="white-space: nowrap;">时间分析：本月响应时间和任务量的24h分布图</span>

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
Average response time per hour this month (disptime - enrtime)

```js
import {hourlyResTime} from './components/dashboard-kpi/hourlyResTime.js'
```

```js
hourlyResTime(dataDis.data.response_time)
```

# 各基地工作负载

Did LFOM transport patient 为yes 的时候，统计airUnit和groundUnit的数量

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



# Transport by Primary Q 指标说明

Transport by Primary Q 用于衡量：病人是否由最合适的资产（Primary asset）且无时间延迟地完成转运。当同时满足"使用预期/最合适资产"与"无延迟"两项条件时记为 Yes，否则记为 No。

Delay Rate（2024.08）展示的是各基地在 2024 年 8 月中 Transport by Primary Q 的比例，用于整体评估不同基地按时、按预期资产完成任务的表现。Delay Reason 针对存在延迟的任务，统计造成延迟的主要原因，用于识别时间维度的瓶颈。

各基地按预期完成比例和各基地未响应原因分析重点关注"是否由最合适资产执行"这一维度，用于评估各基地在资产匹配和调度决策上的表现，并分析未能按预期资产响应的主要原因。


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

# 各基地按预期完成比例与未响应原因说明

本页基于任务的预期与实际执行情况，从"是否由最合适基地执行"角度评估各基地的调度表现。字段 appropriateAsset（Who should have gone if available）表示每个任务最初被分配、预期应执行该任务的基地；字段 respondingAssets 则记录最终实际执行该任务的基地。

图表 Expected Completion Rate by Base (2024) 展示了 2024 年各基地在预期应出任务的总量中，由预期基地实际完成的比例，用于衡量各基地按计划执行任务的能力。同时，对 LF1–LF4 各基地在未能按预期响应的任务中，统计其"未响应原因"占比，用以分析资源占用、维护、距离限制等因素对基地按预期执行任务的影响。
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

# 热力图

<!-- map -->
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
