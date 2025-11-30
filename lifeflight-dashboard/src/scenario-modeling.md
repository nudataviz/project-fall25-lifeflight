---
title: Scenario-modeling
---

# 2 Scenario Modeling

<br/>

<!-- 分析数据 -->

## 2.1 Analysis of the Existing Base

```js
const response = await fetch('http://localhost:5001/api/boxplot')
```

```js
const res = await response.json()
```

```js
const boxplotData = res.data.data
const summary = res.data.summary
```

<div class = 'card' style='width:150px'>

```js
const showOutlier = view(Inputs.toggle({label:'Show outlier',value: true}))
```
</div>

```js
import {boxPlot} from "./components/scenario-modeling/boxPlot.js"
```

```js
boxPlot(boxplotData,showOutlier) 
```

```js
html`<div style="margin-top: 20px;">
  <h3>Vehicle Mileage Statistics</h3>
  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 15px;">
    ${Object.keys(summary || {}).map(veh => {
      const stats = summary[veh];
      const fieldLabels = {
        count: 'Count',
        min: 'Min',
        q1: 'Q1',
        median: 'Median',
        mean: 'Mean',
        q3: 'Q3',
        max: 'Max',
        std: 'Std Dev'
      };
      
      return html`<div class="card">
        <h4>${veh}</h4>
        <table style="width: 100%; border-collapse: collapse;">
          ${Object.entries(stats).map(([key, value]) => {
            const label = fieldLabels[key] || key;
            const displayValue = key === 'count' 
              ? value 
              : `${value.toFixed(2)} miles`;
            return html`<tr>
              <td style="padding: 4px 8px; color: #666;">${label}:</td>
              <td style="padding: 4px 8px; text-align: right; font-weight: 400;">${displayValue}</td>
            </tr>`;
          })}
        </table>
      </div>`;
    })}
  </div>
</div>`
```

<!-- 地图图层 -->
```js
const dataSet = Inputs.radio(["Roux(2012-2023)", "Master(2021-2024)"], {label: "Select a DataSet",value:"Roux(2012-2023)"})
const basePlaceRoux = Inputs.checkbox(['ALL','LF1','LF2','LF3','LF4'], {label: "Select base place",value:['ALL']});
const basePlaceMaster = Inputs.checkbox(['ALL','LF3', 'neoGround', 'LF1', 'L-CCT', 'LF2', 'LF4', 'B-CCT','S-CCT'], {label:"Select base place",value:['ALL']})
```

```js
dataSet
```


```js
const dateSetFile = Generators.input(dataSet)
```

```js
let selectPlaceValue = null
if(dateSetFile=='Roux(2012-2023)'){
  display(basePlaceRoux)
  selectPlaceValue = Generators.input(basePlaceRoux)
}else{
  display(basePlaceMaster)
  selectPlaceValue = Generators.input(basePlaceMaster)
}
```

```js
let mapHtml = null
let mapError = null

if(selectPlaceValue && selectPlaceValue.length > 0){
  try{
    let basePlacesParam = selectPlaceValue.includes('ALL') 
      ? 'ALL' 
      : selectPlaceValue.join(',')
    
    const params = new URLSearchParams({
      dataset: dateSetFile,
      base_places: basePlacesParam
    })
    
    const mapResponse = await fetch(`http://localhost:5001/api/heatmap_by_base?${params}`)
    if(!mapResponse.ok){
      throw new Error(`HTTP ${mapResponse.status}: ${mapResponse.statusText}`)
    }
    mapHtml = await mapResponse.text()
    mapError = null
  }catch(e){
    mapError = e.message
    mapHtml = null
    console.error('Map fetch error:', e)
  }
}
```

```js
html`
    <div class="card" style="overflow: hidden;">
      <h2>Vehicle Base Heatmap</h2>
      <h3 style="color: #666;">
        Heatmap of missions by selected base locations (${dateSetFile})
      </h3>
      <iframe 
        srcdoc=${mapHtml}
        style="width: 100%; height: 500px; border: none;"
        title="Base Heatmap"
      ></iframe>
    </div>
  `
```

接下来分析从出发到接到病人的时间，由于roux数据的时间有问题，这里只选择master的数据来分析。

- 下面这幅图可以看出，每个城市在转运任务上都有自己偏好的基地。，因为城市的散点颜色都较为一致。我们需要重点关注靠右边的这些散点，比如portland，几个运送新生儿的任务用了明显较长的时间，而响应时间快的任务都是有LF3 LF4负责，说明neoGround离protland太远了，可以考虑建一个近的。

```js
const timeDiffResponse = await fetch('http://localhost:5001/api/get_master_response_time')

const response_time = await timeDiffResponse.json() 
```

```js
const responseTimeData = response_time.data || []
```

```js
import {responseTimeChart} from "./components/scenario-modeling/responseTimeChart.js"
```

```js
responseTimeChart(responseTimeData)
```



<!-- 输入输出：
 -->

## 2.2 What-If Scenario Panel

<!-- ```js
// 控制input方法：
// 声明的是input元素
const colors = Inputs.checkbox(["red", "green", "blue"], {label: "Existing Base Locations",value:["red", "green", "blue"]});
// 放置元素
colors
// 取响应式值
const x = Generators.input(colors);
``` -->

```js
const existBase = Inputs.checkbox(['BANGOR', 'LEWISTON', 'SANFORD'], {label: "Existing Base Locations",value:['BANGOR', 'LEWISTON', 'SANFORD']});

const optionalBase = Inputs.checkbox([
        'ROCKPORT', 'AUGUSTA', 'BELFAST', 'WATERVILLE',
        'SKOWHEGAN', 'BRIDGTON', 'PRESQUE ISLE', 'PORTLAND',
        'BIDDEFORD', 'AUBURN'
    ], {label: "Add more Base Locations"});

const serviceRadius = Inputs.range([20,300], {label: "Service Radius (miles)", value: 40, step:1})

const expectedTime = Inputs.range([10,50],{label: "Expected Dispatch-to-Patient Time(Minutes)", value: 20, step:1})
```
```html
${existBase}
${optionalBase}
${serviceRadius}
${expectedTime}
```


```js
const existBaseValue = Generators.input(existBase);
const optionalBaseValue = Generators.input(optionalBase);
const serviceRadiusValue = Generators.input(serviceRadius)
const expectedTimeValue = Generators.input(expectedTime)
```

这里也需要计算时间，所以要用master数据集

## General Base Evaluation 
```js
let rangeMapHtml = null
let rangeMapError = null
let rangeMapStats = null

if(existBaseValue && existBaseValue.length > 0){
  try{
    const allBases = [...existBaseValue, ...(optionalBaseValue || [])]
    
    const params = new URLSearchParams()
    allBases.forEach(base => {
      params.append('baseValue', base)
    })
    params.append('radius', serviceRadiusValue)
    params.append('expectedTime', expectedTimeValue)
    
    const rangeMapResponse = await fetch(`http://localhost:5001/api/get_range_map?${params}`)
    if(!rangeMapResponse.ok){
      throw new Error(`HTTP ${rangeMapResponse.status}: ${rangeMapResponse.statusText}`)
    }
    const rangeMapData = await rangeMapResponse.json()
    rangeMapHtml = rangeMapData.map_html
    rangeMapStats = rangeMapData.statistics
    rangeMapError = null
  }catch(e){
    rangeMapError = e.message
    rangeMapHtml = null
    rangeMapStats = null
    console.error('Range map fetch error:', e)
  }
}
```

```js
// 显示统计信息
if(rangeMapStats){
  display(html`<div style="margin-top: 20px;">
    <h3>Coverage Statistics</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 15px;">
      ${Object.entries(rangeMapStats.coverage_stats || {}).map(([base, count]) => {
        return html`<div class="card">
          <h4>${base}</h4>
          <p style="font-size: 18px; font-weight: bold; color: #2E86C1; margin: 10px 0;">
            ${count} cities covered
          </p>
        </div>`;
      })}
    </div>
    
    <div class="card" style="margin-top: 15px;">
      <h4>Compliance Statistics</h4>
      <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <tr>
          <td style="padding: 8px; color: #666;">Total Tasks:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500;">${rangeMapStats.compliance_stats?.total_tasks || 0}</td>
        </tr>
        <tr>
          <td style="padding: 8px; color: #666;">Compliant Tasks:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500; color: #28B463;">${rangeMapStats.compliance_stats?.compliant_tasks || 0}</td>
        </tr>
        <tr>
          <td style="padding: 8px; color: #666;">Compliance Rate:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500; color: #28B463;">${rangeMapStats.compliance_stats?.compliance_rate?.toFixed(2) || 0}%</td>
        </tr>
        <tr>
          <td style="padding: 8px; color: #666;">Avg Response Time:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500;">${rangeMapStats.compliance_stats?.avg_response_time?.toFixed(2) || 0} minutes</td>
        </tr>
      </table>
    </div>
  </div>`)
}
```


```js
// 显示地图
if(rangeMapError){
  display(html`<div class="card" style="padding: 20px; color: red;">
    <h3>Error loading range map</h3>
    <p>${rangeMapError}</p>
  </div>`)
} else if(rangeMapHtml){
  display(html`
    <div class="card" style="overflow: hidden;">
      <h2>Service Range Map</h2>
      <h3 style="color: #666;">
        Service coverage with ${serviceRadiusValue} mile radius
      </h3>
      <iframe 
        srcdoc=${rangeMapHtml}
        style="width: 100%; height: 500px; border: none;"
        title="Range Map"
      ></iframe>
    </div>
  `)
} else if(!existBaseValue || existBaseValue.length === 0){
  display(html`<div class="card" style="padding: 20px; color: #666;">
    <p>Please select at least one base location to view the range map.</p>
  </div>`)
}
```

## Special Base Evaluation

Special Base: B-CCT, L-CCT, S-CCT, neoGround