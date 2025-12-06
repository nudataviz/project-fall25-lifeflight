import {html} from "../../../_npm/htl@0.3.1/72f4716c.js";

export function rangeMap(heatmapData, baseLocations, radiusMiles) {
  // 处理热力图数据点
  const heatmapPoints = heatmapData
    .map(d => {
      const lat = parseFloat(d.latitude);
      const lon = parseFloat(d.longitude);
      const intensity = parseFloat(d.task_count) || 1;
      return !isNaN(lat) && !isNaN(lon) ? [lat, lon, intensity] : null;
    })
    .filter(p => p !== null);
  
  // 处理基地位置
  const basesJson = JSON.stringify(baseLocations);
  const heatmapPointsJson = JSON.stringify(heatmapPoints);
  
  // 计算地图中心
  let centerLat = 44.5;
  let centerLon = -69.0;
  if (baseLocations.length > 0) {
    centerLat = baseLocations.reduce((sum, b) => sum + b.latitude, 0) / baseLocations.length;
    centerLon = baseLocations.reduce((sum, b) => sum + b.longitude, 0) / baseLocations.length;
  } else if (heatmapPoints.length > 0) {
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
        
        // 添加基地标记和服务半径圆圈
        const bases = ${basesJson};
        const radiusMiles = ${radiusMiles};
        const radiusMeters = radiusMiles * 1609.34; // 转换为米
        
        bases.forEach(base => {
          // 添加基地标记
          L.marker([base.latitude, base.longitude], {
            icon: L.divIcon({
              className: 'base-marker',
              html: '<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
              iconSize: [20, 20],
              iconAnchor: [10, 10]
            })
          })
          .bindPopup('<b>' + base.name + '</b><br>Service Radius: ' + radiusMiles + ' miles')
          .addTo(map);
          
          // 添加服务半径圆圈
          L.circle([base.latitude, base.longitude], {
            radius: radiusMeters,
            color: 'blue',
            fillColor: 'blue',
            fillOpacity: 0.1,
            weight: 2
          })
          .bindPopup(base.name + ' - ' + radiusMiles + ' mile radius')
          .addTo(map);
        });
      </script>
    </body>
    </html>
  `;
  
  return html`<iframe 
    srcdoc=${mapHtml}
    style="width: 100%; height: 500px; border: none;"
    title="Range Map"
  ></iframe>`;
}

