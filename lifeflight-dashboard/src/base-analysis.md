---
title: Current Base Analysis
---
<div class="breadcrumb" style="margin-bottom: 2rem; color: #666; font-size: 0.9rem;">
  <a href="/">Home</a> › 
  <span style="color: #333; font-weight: 500;">What-If: Coverage Optimization</span> › 
  <span style="color: #333; font-weight: 500;">2.1 Existing Base Analysis</span>
</div>

In section 2, we analyze the current base coverage and compare the average Travel Time to Scene before and after the changes.

Only missions that occurred in the state of Maine are included (based on tasks where the pickup city is located in Maine).

# 2.1 Current Base Analysis


<br/>


<!-- ## Vehicle Mileage Statistics
We use the ‘Roux Full Dispatch Data–redacted–v2’ dataset (2012.07–2023.12).
Each record belongs to one of four air bases:
- L1: Bangor Rotor-Wing
- L2: Lewiston Rotor-Wing
- L3: Bangor Fixed-Wing
- L4: Sanford Rotor-Wing

L3 has a much higher median mileage and wider outliers, consistent with its role as a Fixed-Wing base handling longer-distance missions.

L1 has the most missions and the second-highest median mileage, suggesting it is a larger Rotor-Wing base with broader coverage.

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
``` -->

<!-- ```js
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
``` -->

##  Pickup Location Heatmap
The heatmap displays the PU cities associated with each unit.

Because the two datasets cover different time periods and operational units, the dataset and unit type can be selected by the user.

This visualization highlights the mission coverage area for each base.

```js
const dataSet = Inputs.radio(["Roux Full Dispatch Data-redacted-v2.csv(2012-2023)", "FlightTransportsMaster.csv(2021-2024)"], {label: "Select a DataSet",value:"Roux Full Dispatch Data-redacted-v2.csv(2012-2023)"})
const basePlaceRoux = Inputs.checkbox(['ALL','LF1','LF2','LF3','LF4'], {label: "Select Unit Type",value:['ALL']});
const basePlaceMaster = Inputs.checkbox(['ALL','LF3', 'neoGround', 'LF1', 'L-CCT', 'LF2', 'LF4', 'B-CCT','S-CCT'], {label:"Select Unit Type",value:['ALL']})
```

```js
dataSet
```


```js
const dateSetFile = Generators.input(dataSet)
```

```js
let selectPlaceValue = null
if(dateSetFile=='Roux Full Dispatch Data-redacted-v2.csv(2012-2023)'){
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

## Response Time Analysis (Base → Patient Location)
<div class="note" label='Data Notes'>

- Only the *FlightTransportsMaster.csv(2021-2024)* dataset is used, as the *Roux Full Dispatch Data-redacted-v2.csv(2012-2023)* dataset contains inconsistent date formats that affect cross-day missions.
- Response time is calculated as *enrtime* – *atstime* (vehicle departure to arrival at patient location).
- Only cities with more than 10 missions are included.

</div>


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
responseTimeData
```
```js
responseTimeChart(responseTimeData)
```

This chart examines whether certain cities have longer response times because they are farther from a specific base.

Cities show clear preferences for specific bases, indicated by the consistent point colors within each city. The rightmost points on each horizontal line highlight missions with the longest en-route times. 

For example, Portland shows several neonatal transports with much longer travel times handled by neoGround, while faster missions were completed by LF3 and LF4. This pattern suggests that neoGround is relatively distant from Portland, indicating potential value in establishing a closer base.


<div class='note' label='Presentation Question'>
Previously, we used <span style=' font-size: 0.95rem; padding: 0.15rem 0.4rem; border-radius: 6px; border: 1px solid #d0d7de; background:white;'> Plot.normalizeX </span> to normalize the data. This made the charts look cleaner and helped us compare patterns within each city. But we later found a problem: the normalized values can’t really be compared across different cities, because each city is normalized based on its own total.

For example, if a city has longer response times (like 20–60 minutes), its normalized values might end up smaller. Another city with shorter response times (like 5–15 minutes) might get larger normalized values.
So when we sort by the normalized values, a city with longer actual response times could appear earlier, and a city with shorter times could appear later. That doesn’t really make sense.

So we decided to remove normalization and just use the raw response time (in minutes). This way, the sorting correctly matches the actual response times.
</div>