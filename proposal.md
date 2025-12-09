# ProjectName
FlightPath Dashboard

# Story

We are prototyping an interactive analytics dashboard to help LifeFlight explore its historical operations, 

forecast emergency medical demand over a multi-year horizon, and compare alternative resource allocation scenarios 

(such as different base locations and service radii).

The prototype focuses on:

- visualizing current mission volume, response times, and base workload,

- using a Prophet time-series model with selected demographic variables to forecast future mission demand, and

- providing interactive maps to compare service coverage and response times under different base layout scenarios.

The goal is not to deliver a production optimization engine, but to offer a transparent, data-driven decision support tool 

that LifeFlight staff can build on in future work.

# Stakeholder
Dan Koloski (Initial Contact), LifeFlight Staff (Users)

---

# Team
## Members
- [Shenyu Li] (Team Lead)
- [Yantong Guo]

## Repo
https://github.com/nudataviz/project-fall25-lishenyu1024

---

# Data
## Describe
We primarily use historical and current **LifeFlight operational data** 

(including transport volume, pickup locations, bases, and asset type) and augment it with a limited set of external data:

- **Population and demographic data** (historical and projections at the county/city level)

- **Age structure** variables used as external regressors in the forecasting model

- **Public weather history sources** explored as potential future regressors

In the current prototype, demographic variables are integrated into the forecasting model.  

Weather data is documented as a possible extension but is not yet fully incorporated into the model.

## Link / Risks
The core operational data is available in a **SharePoint** repository accessible via Dan Koloski.  

The main risk is the complexity of cleaning and aligning multiple external datasets (population, demographics, weather) 

and the limited time to fully integrate them into robust long-term forecasting and scenario simulations.

---

# Scope & Objectives (Current Prototype)

## Implemented Features

### 1. Current Operations & Service Quality Analysis

- Mission volume by weekday and hour

- Dispatch/response time distribution

- Base workload comparison across air and ground units

- "Transport by Primary Q" analysis (appropriate asset without delay)

- Expected completion rate and no-response reason analysis

### 2. Mid- to Long-Term Demand Forecasting

- Multi-year mission volume forecasting using a Prophet time-series model

- External regressors based on demographic / age-structure data

- Seasonality analysis via weekday/hour heatmaps

- Model performance metrics (MAE, MAPE, RMSE)

### 3. Scenario Simulation of Base Layout and Service Scope

- Interactive coverage map with existing and candidate base locations

- Adjustable service radius for scenario comparison

- Response time analysis by city and base

- Ground-unit-specific coverage analysis (e.g., neoGround)

## Technical Implementation

- **Backend:** Flask REST API providing processed data and forecast endpoints

- **Frontend:** Observable Framework interactive dashboard

- **Deployment:** GitHub Pages (static build served from `docs/`)

---

# Visualization Plan (by category)
**Total: 3 categories, 10+ core visuals** implemented as a working prototype.

## 1) Current Operations & Service Quality Dashboard

### 1.1 Mission Volume Distribution (Weekday × Hour Heatmap)
- **Implementation:** Aggregates historical missions by weekday and hour to identify peak demand periods.
- **Visualization:** Heatmap showing mission volume patterns across time dimensions.

### 1.2 Response Time Analysis (Hourly Distribution)
- **Implementation:** Displays average response time (dispatch time - enroute time) by hour of day for the current month.
- **Visualization:** Line chart showing response time patterns throughout the day.

### 1.3 Base Workload Analysis
- **Implementation:** Compares workload across different bases (air units and ground units).
- **Visualization:** Bar/area charts showing workload distribution by base.

### 1.4 Transport by Primary Q Analysis
- **Implementation:** Analyzes the `transportByPrimaryQ` field to measure whether patients were transported by the most appropriate asset without delay.
- **Visualization:** 
  - Delay Rate chart showing the proportion of "Yes" responses by base
  - Delay Reason chart showing causes of delays when conditions are not met

### 1.5 Expected Completion Rate & No Response Reasons
- **Implementation:** Evaluates whether tasks were completed by the expected base (`appropriateAsset` vs `respondingAssets`).
- **Visualization:**
  - Expected Completion Rate by Base chart
  - No Response Reasons by Base chart showing why expected bases did not respond

---

## 2) Demand Forecasting

### 2.1 Demand Forecast (multi-year)
- **Implementation:** Uses a Prophet time-series model with demographic regressors to forecast mission volume.
- **Model Features:** 
  - Integration of age-structure variables derived from population data
  - Reports MAE, MAPE, and RMSE for model evaluation
- **Visualization:** Line chart with historical and forecasted mission volume, including confidence intervals.

### 2.2 Seasonality & Day-of-Week/Hour Heatmap
- **Implementation:** Aggregates historical missions by weekday and hour to reveal cyclical patterns.
- **Visualization:** Heatmap showing long-term demand patterns across time dimensions.

---

## 3) Scenario Modeling & Base Layout

### 3.1 Interactive Coverage Map
- **Implementation:** Interactive map allowing users to toggle existing and candidate base locations and adjust service radius for scenario comparison.
- **Features:**
  - Real-time coverage visualization
  - Comparison of coverage under different base configurations
- **Visualization:** Interactive map with coverage areas and base location markers.

### 3.2 Response Time by City
- **Implementation:** Analyzes city-level response times by base to identify locations with significantly longer response times.
- **Visualization:** Chart/map showing response time patterns across different cities and bases.

### 3.3 Ground Unit Service Coverage
- **Implementation:** Ground-unit-specific analysis estimating typical speeds, coverage radius, and compliance rates for units such as neoGround.
- **Visualization:** Coverage map and metrics specific to ground transport units.

---

# Technical Approach

We align variable definitions and some metric conventions with **Dan Koloski's prior methodology and deliverables** to maintain comparability.  

We also reference approaches in published aeromedical research (e.g., Jo Røislien, NZ/AU examples) for handling seasonality, spatial coverage, 

and response-time analysis, adapting them to the scope of this prototype.

---

# KPIs & Success Metrics

In the current prototype, the dashboard focuses on:

- Mission volume (overall and by time of week)

- Base workload distribution

- Dispatch/response time metrics

- Proportion of missions completed by the expected base

- Coverage and compliance metrics in scenario simulations

Additional KPIs such as unit cost, fleet utilization, or safety incident rates are documented as potential extensions 

but are not implemented in this version.

---

# Summary of Visuals (Implemented)
- **Current Operations & Service Quality Dashboard:** 5+ charts
- **Demand Forecasting:** 2 charts
- **Scenario Modeling & Base Layout:** 3+ interactive visualizations
**Total:** **10+ core visualizations** implemented and functional

---