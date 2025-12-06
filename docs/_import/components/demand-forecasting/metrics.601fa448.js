import {html} from "../../../_npm/htl@0.3.1/72f4716c.js";

export function calculateMetrics(cv_metrics){
  if(cv_metrics){
    const metrics = cv_metrics
    return html`
      <div class="card">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr);">          
          <div style="padding: 1rem; border-radius: 8px;">
            <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">MAE</div>
            <div style="font-size: 1.5rem; font-weight: bold;">
              ${metrics.mae.toFixed(2)}
            </div>
            <div style="font-size: 0.75rem; color: grey;">
              Mean Absolute Error
            </div>
          </div>
          
          <div style="padding: 1rem; border-radius: 8px;">
            <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">MAPE</div>
            <div style="font-size: 1.5rem; font-weight: bold;">
              ${(metrics.mape * 100).toFixed(2)}%
            </div>
            <div style="font-size: 0.75rem;color: grey;">
              Mean Absolute Percentage Error
            </div>
          </div>
          
          <div style="padding: 1rem; border-radius: 8px;">
            <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">RMSE</div>
            <div style="font-size: 1.5rem; font-weight: bold;">
              ${metrics.rmse.toFixed(2)}
            </div>
            <div style="font-size: 0.75rem; color: grey;">
              Root Mean Squared Error
            </div>
          </div>
        </div>
      </div>
    `
  }}