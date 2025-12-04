import {html} from "npm:htl";

export function fountainsHeatmap(fuentes) {
  // 处理数据点
  const fuentesPoints = fuentes
    .map(d => {
      const lat = parseFloat(d.latitud);
      const lon = parseFloat(d.longitud);
      return !isNaN(lat) && !isNaN(lon) ? [lat, lon, 1] : null;
    })
    .filter(p => p !== null);
  
  const pointsJson = JSON.stringify(fuentesPoints);
  
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
        const map = L.map('map').setView([40.4167754, -3.7037902], 13);
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png', {
          attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        const points = ${pointsJson};
        
        L.heatLayer(points, {
          radius: 25,
          blur: 15,
          maxZoom: 17,
          max: 1.0,
          gradient: {
            0.4: 'blue',
            0.6: 'cyan',
            0.7: 'lime',
            0.8: 'yellow',
            1.0: 'red'
          }
        }).addTo(map);
      </script>
    </body>
    </html>
  `;
  
  return html`<iframe 
    srcdoc=${mapHtml}
    style="width: 100%; height: 500px; border: none;"
    title="Fountains Heatmap"
  ></iframe>`;
}