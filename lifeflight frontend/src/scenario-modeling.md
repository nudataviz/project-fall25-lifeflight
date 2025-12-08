---
title: "Service Coverage: All Units"
---

<div class="breadcrumb" style="margin-bottom: 2rem; color: #666; font-size: 0.9rem;">
  <a href="/">Home</a> › 
  <span style="color: #333; font-weight: 500;">What-If: Coverage Optimization</span> › 
  <span style="color: #333; font-weight: 500;">2.2 Service Coverage: All Units</span>
</div>


# 2.2 Service Coverage: All Units
<div class="note" label="Data Notes">

- This analysis uses the *FlightTransportsMaster.csv(2021-2024)* as it involves time-based calculations.
- LifeFlight operates three bases: Bangor, Lewiston, and Sanford ([LifeFlight Website](https://lifeflightmaine.org/our-services/helicopter-transport/)).
- City coordinates are used as approximate base locations.
- Optional Base Locations are selected from cities with higher mission volumes.
</div>

## Input Parameters
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
<!-- ${expectedTime} -->
```


```js
const existBaseValue = Generators.input(existBase);
const optionalBaseValue = Generators.input(optionalBase);
const serviceRadiusValue = Generators.input(serviceRadius)
const expectedTimeValue = Generators.input(expectedTime)
```


```js
import {rangeMap} from './components/scenario-modeling/rangeMap.js'
```

```js
let rangeMapData = null
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
    params.append('expectedTime', expectedTimeValue||20)
    
    const rangeMapResponse = await fetch(`http://localhost:5001/api/get_range_map?${params}`)
    if(!rangeMapResponse.ok){
      throw new Error(`HTTP ${rangeMapResponse.status}: ${rangeMapResponse.statusText}`)
    }
    const responseData = await rangeMapResponse.json()
    rangeMapData = {
      heatmapData: responseData.heatmap_data || [],
      baseLocations: responseData.base_locations || []
    }
    rangeMapStats = responseData.statistics
    rangeMapError = null
  }catch(e){
    rangeMapError = e.message
    rangeMapData = null
    rangeMapStats = null
    console.error('Range map fetch error:', e)
  }
}
```

```js
if(rangeMapError){
  display(html`<div class="card" style="padding: 20px; color: red;">
    <h3>Error loading range map</h3>
    <p>${rangeMapError}</p>
  </div>`)
} else if(rangeMapData){
  display(html`
    <div class="card" style="overflow: hidden;">
      <h2>Service Range Map</h2>
      <h3 style="color: #666;">
        Service coverage with ${serviceRadiusValue} mile radius
      </h3>
      ${rangeMap(rangeMapData.heatmapData, rangeMapData.baseLocations, serviceRadiusValue)}
    </div>
  `)
} else if(!existBaseValue || existBaseValue.length === 0){
  display(html`<div class="card" style="padding: 20px; color: #666;">
    <p>Please select at least one base location to view the range map.</p>
  </div>`)
}
```
<div style="margin-top: 20px;">
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

<!-- ## Coverage Statistics
```js
if(rangeMapStats){
  display(html`<div style="margin-top: 20px;">
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
``` -->


