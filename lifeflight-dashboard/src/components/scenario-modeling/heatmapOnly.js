import {html} from "npm:htl";

export function heatmapOnly(heatmapData) {
  // 处理热力图数据点
  const heatmapPoints = heatmapData
    .map(d => {
      const lat = parseFloat(d.latitude);
      const lon = parseFloat(d.longitude);
      const intensity = parseFloat(d.task_count) || 1;
      return !isNaN(lat) && !isNaN(lon) ? [lat, lon, intensity] : null;
    })
    .filter(p => p !== null);
  
  const heatmapPointsJson = JSON.stringify(heatmapPoints);
  
  // 计算地图中心
  let centerLat = 44.5;
  let centerLon = -69.0;
  if (heatmapPoints.length > 0) {
    centerLat = heatmapPoints.reduce((sum, p) => sum + p[0], 0) / heatmapPoints.length;
    centerLon = heatmapPoints.reduce((sum, p) => sum + p[1], 0) / heatmapPoints.length;
  }
  
  // 创建完整的 HTML 文档
  const mapHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css" />
      <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
      <style>
        body { margin: 0; padding: 0; }
        #map { width: 100%; height: 100vh; }
      </style>
    </head>
    <body>
      <div id="map"></div>
      <script>
        const map = L.map('map').setView([${centerLat}, ${centerLon}], 7);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // 添加热力图
        const heatmapPoints = ${heatmapPointsJson};
        if (heatmapPoints.length > 0) {
          L.heatLayer(heatmapPoints, {
            radius: 12,
            blur: 12,
            maxZoom: 18,
            minOpacity: 0.3
          }).addTo(map);
        }
      </script>
    </body>
    </html>
  `;
  
  return html`<iframe 
    srcdoc=${mapHtml}
    style="width: 100%; height: 500px; border: none;"
    title="Heatmap"
  ></iframe>`;
}

