---
title: Scenario-modeling
---

# 1 Scenario Modeling

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
// 获取地图 HTML
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

接下来分析从出发到接到病人的时间，由于roux数据的时间有问题，这里只选择master的数据来分析







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
const serviceRadius = Inputs.range([20,350], {label: "Service Radius (miles)", value: 50, step:1})
```

${existBase}
${optionalBase}
${serviceRadius}


% s>>>
```js
const existBaseValue = Generators.input(existBase);
const optionalBaseValue = Generators.input(optionalBase);
const serviceRadiusValue = Generators.input(serviceRadius)
```
```js
display(existBaseValue)
display(optionalBaseValue)
```
