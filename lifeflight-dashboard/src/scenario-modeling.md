---
title: Scenario-modeling
---

# 1 Scenario Modeling

<br/>

<!-- 分析数据 -->

## 2.1 Vehicle Mileage Distribution

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

```js
import {boxPlot} from "./components/scenario-modeling/boxPlot.js"
```

```js
boxPlot(boxplotData) 
```

```js
// 使用 HTML 显示统计摘要信息
html`<div style="margin-top: 20px;">
  <h3>Vehicle Mileage Statistics</h3>
  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 15px;">
    ${Object.keys(summary || {}).map(veh => {
      const stats = summary[veh];
      // 定义字段名称映射
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



<!-- 输入输出 -->

## 2.2 What-If Scenario Panel