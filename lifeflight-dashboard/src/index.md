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
dataDis
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
dataBase
```

```js
import {baseWorkloadPlot} from './components/dashboard-kpi/baseWorkloadPlot.js'
```

```js
baseWorkloadPlot(dataBase.data)
```



# Transport by Primary Q

分析transportByPrimaryQ字段。：最合适的资产（飞机/车辆）是否无延迟地运输了病人. 字段数值是yes/no
有两种情况：
- 1是否是最合适的资产去运输病人
- 2是否有延迟

当这两点都满足的时候才是yes。否则是no。

Delay Rate(2024.08)展示的就是每个基地这个字段transportByPrimaryQ的比例。

- Delay Reason统计的delay的原因。（展示第二点）
- 后面的各基地按预期完成比例和各基地没有响应的原因分析 是在分析第一点（1是否是最合适的资产去运输病人）


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

# <span style="white-space: nowrap;">各基地按预期完成比例和各基地没有响应的原因分析</span>


- appropriateAsset (Who should have gone if available)： 这个字段是每个任务初始被分配的任务。
- respondingAssets：但不是每个基地都能去的，这个字段是最终执行任务的基地。
- Expected Completion Rate by Base (2024)就展示了，按预期基地完成任务的比例

展示每个基地预期要出任务的数量，以及按照预期完成的比例

<div class='card'>
${expectedCompletionPlot(data.expectedCompletionData)}
</div>

展示LF1-LF4各基地没有响应的原因占比

```js
import {noResponseReasonPlot} from './components/dashboard-kpi/noResponseReasonPlot.js'
```

<div class='card'>
${noResponseReasonPlot(data.noResponseReasonsData)}
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
