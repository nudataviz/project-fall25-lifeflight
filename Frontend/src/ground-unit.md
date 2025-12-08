---
title: "Service Coverage: Ground Units"
---

<div class="breadcrumb" style="margin-bottom: 2rem; color: #666; font-size: 0.9rem;">
  <a href="/">Home</a> › 
  <span style="color: #333; font-weight: 500;">What-If: Coverage Optimization</span> › 
  <span style="color: #333; font-weight: 500;">2.3 Service Coverage: Ground Units</span>
</div>

# 2.3 Service Coverage: Ground Units
<div class="note" label="Data Notes">

- This analysis uses the *FlightTransportsMaster.csv(2021-2024)* as it involves time-based calculations.
- Ground units’ missions are highly concentrated near their bases. Longer missions, especially for neoGround, result in significantly increased response times. This makes the base location of Ground Units more critical than Air Units, warranting a separate analysis.
- Ground Units included: B-CCT, L-CCT, S-CCT, neoGround.(B-CCT, L-CCT, and S-CCT are the same type of unit but at different locations. However, considering possible differences in base configuration, they are treated as separate types here.)

</div>

## Speed Analysis

Median speed is calculated for each base to estimate the typical mission speed from base to patient location.
```js
const speedsResponse = await fetch('http://localhost:5001/api/get_special_base_speeds')
const speedsData = await speedsResponse.json()
const baseSpeeds = speedsData.speeds || {}
```

<div class='grid' style='grid-template-columns: 1fr 2fr;'>
<div class="card" style="margin-top:20px;height: 70%;">
    <h3>Ground Unit Speed Statistics</h3>
    <table style="width: 100%; border-collapse: collapse;">
      ${Object.entries(baseSpeeds).map(([base, speed]) => {
        return html`<tr>
          <td style="padding: 8px; color: #666;">${base}:</td>
          <td style="padding: 8px; text-align: right; font-weight: 500;">${speed.toFixed(2)} mph</td>
        </tr>`;
      })}
    </table>
  </div>
<div class="note" label="Calculation Notes">

- Speed for each unit is estimated using the median speed of its past missions.
- Distance between cities is calculated from city coordinates.
- Service time for each mission is computed as distance ÷ speed.
</div>
</div>

## Select Ground Unit Type
Choose the Ground Unit type to analyze.

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
     // get base city
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
    
    
  </div>`)
}
```
<!-- <div class="note" label="Metrics">

- Cities Covered: Number of cities within the unit’s service range.
- Compliance Statistics: Compares the total number of missions in coverage with the number of missions meeting response-time standards.
</div> -->
<div class='grid' style='grid-template-columns: 1fr 2fr;'>
<div class="card" style="height: 70%;margin-top:15px">
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
<div class="note" label="Calculation Notes">

- Adding a new base recalculates service coverage and arrival times.
- If coverage areas overlap, the shorter arrival time is used.
</div>


<div>


