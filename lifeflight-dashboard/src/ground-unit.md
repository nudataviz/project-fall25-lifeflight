---
title: "Service Coverage: Ground Units"
---

<div class="breadcrumb" style="margin-bottom: 2rem; color: #666; font-size: 0.9rem;">
  <a href="/">Home</a> › 
  <span style="color: #333; font-weight: 500;">What-If: Coverage Optimization</span> › 
  <span style="color: #333; font-weight: 500;">2.3 Service Coverage: Ground Units</span>
</div>

# 2.3 Service Coverage: Ground Units
数据说明：
- 涉及时间计算，所以用master数据集（2021.8-2024.8）

地面救援里距离对时间的影响更大。我们发现数据集中，Ground Unit负责的任务都集中在Unit周围，当任务距离较远的时候，接到病人的时间会明显增加（尤其是对于neoGround)，所以Ground Unit的位置比air Unit更加重要，单独拿出来分析。
Ground Unit: B-CCT, L-CCT, S-CCT, neoGround

## 每个基地前往病人所在地的速度

统计每个基地前往病人所在地的速度，用速度的中位数作为每种基地的出任务速度的估计。
```js
const speedsResponse = await fetch('http://localhost:5001/api/get_special_base_speeds')
const speedsData = await speedsResponse.json()
const baseSpeeds = speedsData.speeds || {}
```

```js
if(Object.keys(baseSpeeds).length > 0){
  display(html`<div class="card" style="margin-top: 20px;width: 50%">
    <h3>Ground Unit Speed Statistics</h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
      ${Object.entries(baseSpeeds).map(([base, speed]) => {
        return html`<tr>
          <td style="padding: 8px; color: #666;">${base}:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500;">${speed.toFixed(2)} mph</td>
        </tr>`;
      })}
    </table>
  </div>`)
}
```

## Select Ground Unit Type
选择你想分析的Ground Unit 类型
```js

const centerType = Inputs.radio(['neoGround', 'L-CCT', 'B-CCT', 'S-CCT'], {
  label: "Select Center Type",
  value: 'neoGround'
})
```

```js
centerType
```

```js
const selectedCenterType = Generators.input(centerType)
```

```js
const specialBaseRadius = Inputs.range([20, 300], {label: "Service Radius (miles)", value: 50, step: 1})
const specialBaseExpectedTime = Inputs.range([10, 50], {label: "Expected Dispatch-to-Patient Time (Minutes)", value: 20, step: 1})
```

```html
${specialBaseRadius}
${specialBaseExpectedTime}
```

```js
const specialBaseRadiusValue = Generators.input(specialBaseRadius)
const specialBaseExpectedTimeValue = Generators.input(specialBaseExpectedTime)
```

```js
const citiesResponse = await fetch('http://localhost:5001/api/get_maine_cities')
const citiesData = await citiesResponse.json()
const maineCities = citiesData.cities || []
const maineCitiesSet = new Set(maineCities.map(c => c.toUpperCase().trim()))
```

```js
let initialBaseCity = null
if(selectedCenterType){
  try{
    const tempParams = new URLSearchParams({
      centerType: selectedCenterType,
      radius: 50,
      expectedTime: 20
    })
    const tempResponse = await fetch(`http://localhost:5001/api/get_special_base_statistics?${tempParams}`)
    if(tempResponse.ok){
      const tempData = await tempResponse.json()
      // 从coverage_stats中获取初始base城市
      const coverageStats = tempData.statistics?.coverage_stats || {}
      initialBaseCity = Object.keys(coverageStats)[0] || null
    }
  }catch(e){
    console.error('Error getting initial base city:', e)
  }
}

```


```js
const cityTextarea = Inputs.textarea({
  label: "Base Cities (comma-separated)",
  placeholder: "Enter city names separated by commas (e.g., PORTLAND, BANGOR)",
  value: initialBaseCity || "",
  rows: 4,
  submit: true
})
```


```js
cityTextarea
```

```js
const cityTextareaValue = Generators.input(cityTextarea)
```

```js
import {rangeMap} from './components/scenario-modeling/rangeMap.js'
```

```js
// 获取special base统计信息
let specialBaseMapData = null
let specialBaseStats = null
let specialBaseError = null

if(selectedCenterType){
  try{
    const params = new URLSearchParams({
      centerType: selectedCenterType,
      radius: specialBaseRadiusValue,
      expectedTime: specialBaseExpectedTimeValue
    })
    
    if(cityTextareaValue && typeof cityTextareaValue === 'string' && cityTextareaValue.trim()){
      params.append('baseCities', cityTextareaValue)
    }
    
    const specialBaseResponse = await fetch(`http://localhost:5001/api/get_special_base_statistics?${params}`)
    if(!specialBaseResponse.ok){
      throw new Error(`HTTP ${specialBaseResponse.status}: ${specialBaseResponse.statusText}`)
    }
    const responseData = await specialBaseResponse.json()
    specialBaseMapData = {
      heatmapData: responseData.heatmap_data || [],
      baseLocations: responseData.base_locations || []
    }
    specialBaseStats = responseData.statistics
    specialBaseError = null
  }catch(e){
    specialBaseError = e.message
    specialBaseMapData = null
    specialBaseStats = null
    console.error('Special base fetch error:', e)
  }
}
```
## Ground Unit Statistics - ${selectedCenterType}

计算说明：
- 使用对每种Unit估算的Speed作为speed，城市和城市的坐标计算出的距离作为距离，来计算服务半径内的任务从基地出发到达用户的时间。
- 每当加入一个新的基地，会重新计算新基地覆盖范围内的到达时间。
- 如果两个基地的覆盖范围有重合，会取时间小的。


指标说明：

- 统计出所选base在服务范围下cover的城市数量，Compliance Statistics对比了范围内的任务数量和响应时间达标的任务数量。


```js
if(specialBaseStats){
  display(html`<div style="margin-top: 20px;">   
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 15px;">
      ${Object.entries(specialBaseStats.coverage_stats || {}).map(([base, count]) => {
        return html`<div class="card">
          <h4>${base}</h4>
          <p style="font-size: 18px; font-weight: bold; color: #2E86C1; margin: 10px 0;">
            ${count} cities covered
          </p>
        </div>`;
      })}
    </div>
    
    <div class="card" style="width: 50%">
      <h4>Compliance Statistics</h4>
      <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <tr>
          <td style="padding: 8px; color: #666;">Total Tasks:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500;">${specialBaseStats.compliance_stats?.total_tasks || 0}</td>
        </tr>
        <tr>
          <td style="padding: 8px; color: #666;">Compliant Tasks:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500; color: #28B463;">${specialBaseStats.compliance_stats?.compliant_tasks || 0}</td>
        </tr>
        <tr>
          <td style="padding: 8px; color: #666;">Compliance Rate:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500; color: #28B463;">${specialBaseStats.compliance_stats?.compliance_rate?.toFixed(2) || 0}%</td>
        </tr>
        <tr>
          <td style="padding: 8px; color: #666;">Avg Response Time:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500;">${specialBaseStats.compliance_stats?.avg_response_time?.toFixed(2) || 0} minutes</td>
        </tr>
      </table>
    </div>
  </div>`)
}
```

```js
if(specialBaseError){
  display(html`<div class="card" style="padding: 20px; color: red;">
    <h3>Error loading Ground Unit map</h3>
    <p>${specialBaseError}</p>
  </div>`)
} else if(specialBaseMapData){
  display(html`
    <div class="card" style="overflow: hidden;">
      <h2>Ground Unit Range Map - ${selectedCenterType}</h2>
      <h3 style="color: #666;">
        Service coverage with ${specialBaseRadiusValue} mile radius
        ${cityTextareaValue && cityTextareaValue.trim() ? `(Base Cities: ${cityTextareaValue})` : ''}
      </h3>
      ${rangeMap(specialBaseMapData.heatmapData, specialBaseMapData.baseLocations, specialBaseRadiusValue)}
    </div>
  `)
} else if(!selectedCenterType){
  display(html`<div class="card" style="padding: 20px; color: #666;">
    <p>Please select a center type to view the map.</p>
  </div>`)
}
```


