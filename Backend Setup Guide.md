
# LifeFlight Dashboard – Backend

This repository contains the backend API for the LifeFlight dashboard.

---

## Requirements

- **Python 3.8 or newer**

-----

## Setup

Navigate into the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:
**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

-----

## Running the Server

Start the backend:

```bash
python app.py
```

The server will run at:

```
http://localhost:5001
```

Test endpoint:

```
http://localhost:5001/api/test
```


## Project Structure

```
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
```

