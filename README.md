# Lifeflight Dashboard
An interactive data visualization dashboard for analyzing medical transport services data.
# Current Feature
- Interactive geographic visualizations using Folium maps. 
- Time series forecasting with Prophet for demand prediction.
- Hour-by-weekday heatmap visualization.
# Tech Stack
### Backend:
- Python with Flask framework
### Frontend:
- Observable Framework
### Prerequisites
- **Python 3.9 or higher** (developed with Python 3.12)
- **Node.js 18 or higher** (developed with Node.js 23)

# Setup Instructions
### Backend Setup
- Navigate to the backend directory:
```bash
cd backend
```
- Create and activate a virtual environment(for Mac):
```bash
python -m venv venv
source venv/bin/activate
```
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Start the backend server:
```bash
python app.py
```
- The backend API will be available at:
```bash
http://localhost:5001/
```

### Frontend
- Navigate to the frontend directory:
```bash
cd lifeflight-dashboard
```
- Install Node.js dependencies:
```bash
npm install
```

- Start the development server:
```bash
npm run dev
```


- The frontend will be available at:
```bash
http://127.0.0.1:3000/
```

# Extra Data Sources
- **Maine Population Projections**:：https://www.maine.gov/dafs/economist/demographic-projections
- **Historical Population Data**：https://www.census.gov/data/developers/data-sets/acs-1year.html

