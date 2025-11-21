# LifeFlight Dashboard – Frontend

This repository contains the frontend application for the LifeFlight dashboard MVP.

---

## Requirements

- Node.js **16 or newer**

Check your version:
```bash
node -v
```

---

## Setup

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npm start
```

The application will be available at:
```
http://localhost:3000
```

---

## Backend Connection

The frontend expects the backend API to run locally on **port 5001**.

If your backend uses a different port, update the API base URLs in:

- `src/scenes/dashboard/index.jsx`
- `src/components/LineChart.jsx`
- `src/components/HistogramChart.jsx`
- `src/components/HeatMap.jsx`

---

## Project Structure

```
src/
  components/
  scenes/
  data/
  App.js
  index.js
```

---


