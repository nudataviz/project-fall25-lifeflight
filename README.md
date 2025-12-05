# Lifeflight Dashboard

An interactive data visualization dashboard for analyzing medical transport services data.

# Current Features

- Time series forecasting with Prophet for demand prediction.
- Hour-by-weekday heatmap visualization.

# Tech Stack

### Backend:
- Python with Flask framework (see backend/requirements.txt)
- Requires Python 3.9 or higher (developed with Python 3.12)

### Frontend:
- Observable Framework
- Requires Node.js 18 or higher (developed with Node.js 23)

### Start the backend
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
The backend API will be available at: `http://localhost:5001/`

### Start the Framework app

```
cd lifeflight-dashboard
npm run dev
```
The frontend will be available at: `http://127.0.0.1:3000/ `

# Data Sources

- **Maine Population Projections**:：https://www.maine.gov/dafs/economist/demographic-projections
- **Historical Population Data**：https://www.census.gov/data/developers/data-sets/acs-1year.html
- **Total Population for Maine Counties (2010-2019)**: https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-total.html
- **Maine Weather History**: https://www.wunderground.com/history/daily/US/ME/4210/date/2024-9-20

