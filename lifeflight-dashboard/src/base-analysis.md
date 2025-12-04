---
title: Existing Base Analysis
---
<div class="breadcrumb" style="margin-bottom: 2rem; color: #666; font-size: 0.9rem;">
  <a href="/">Home</a> › 
  <span style="color: #333; font-weight: 500;">What-If: Coverage Optimization</span> › 
  <span style="color: #333; font-weight: 500;">2.1 Existing Base Analysis</span>
</div>

# 2.1 Existing Base Analysis
在这一节中，我们专注于分析Maine州的任务
<br/>



## Vehicle Mileage Statistics
roux数据集中（2012.07-2023.12），每个航空基地任务的历程统计。
这里L1 is Bangor RotorWing, L2 is Lewiston RW, L3 is Bangor FixedWing, L4 is Sanford RW

LF3 的所属基地因为是Fixed-Wing基地所以飞的比较远。中位数为158miles。而其他三个基地都是RotorWing，所以中位数在50miles左右。（这里取中位数是因为防止个别较远的任务影响平均值）。
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
##  任务起始地热力图
接下来在展示每个基地所属vehicle负责任务的PU city热力图。

因为没有数据文件里没有直接给出每个单位的所属地点，根据热力图，我们能大概估计出每个单位的所在城市。
可以选择想要分析的数据文件，因为这两个文件跨时间不同，而且包含基地也不一样，所以我们就分开来展示了。

有趣的发现：在roux文件里，LF3基地的中心是在bangor，但是更新的数据表现出LF3基地似乎移动至caribou.

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
import {heatmapOnly} from './components/scenario-modeling/heatmapOnly.js'
```

```js
let mapData = null
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
    const responseData = await mapResponse.json()
    mapData = responseData.heatmap_data || []
    mapError = null
  }catch(e){
    mapError = e.message
    mapData = null
    console.error('Map fetch error:', e)
  }
}
```

```js
if(mapError){
  display(html`<div class="card" style="padding: 20px; color: red;">
    <h3>Error loading heatmap</h3>
    <p>${mapError}</p>
  </div>`)
} else if(mapData && mapData.length > 0){
  display(html`
    <div class="card" style="overflow: hidden;">
      <h2>Vehicle Base Heatmap</h2>
      <h3 style="color: #666;">
        Heatmap of missions by selected base locations (${dateSetFile})
      </h3>
      ${heatmapOnly(mapData)}
    </div>
  `)
} else if(selectPlaceValue && selectPlaceValue.length > 0){
  display(html`<div class="card" style="padding: 20px; color: #666;">
    <p>No data available for selected base locations.</p>
  </div>`)
}
```

## 从基地出发-接到病人时间分析
数据说明：

- 由于roux数据的时间的日期比较混乱，处理跨日任务的时候有问题。所以这里只选择master文件（2021.8-2023.8）的数据来分析。
- 所选字段：enrtime（车辆出发时间）- atstime（到达患者所在地时间）
- 只显示有10个样本以上的城市

通过这幅图主要想显示出，是否有一些任务，因为病人所在的城市离特定的基地远，导致响应时间长。
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

