# LifeFlight Dashboard – Backend

This repository contains the backend API for the LifeFlight dashboard MVP. 

## Requirements
- Python 3.8 or newer  
Check your version with: python3 --version

## Setup

Navigate into the backend directory:
cd backend

Create and activate a virtual environment:
macOS/Linux:
python3 -m venv venv
source venv/bin/activate

Windows:
python -m venv venv
venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

## Running the Server

Start the backend:
python app.py

The server will run at:
http://localhost:5001

Test endpoint:
http://localhost:5001/api/test

## Available Endpoints

- GET /api/test — Test server status  
- GET /api/indicators — Dashboard indicators  
- GET /api/veh_count — Vehicle count statistics  
- GET /api/hourly_departure — Hourly departure density  
- GET /api/heatmap — Heatmap HTML output  

## Project Structure

backend/  
├── app.py  
├── requirements.txt  
├── config.py  
├── data/  
│   ├── data.csv  
│   └── city_coordinates.json  
└── utils/  
    ├── getData.py  
    ├── heatmap.py  
    ├── responseTime.py  
    └── veh_count.py  


