# ProjectName
FlightPath Dashboard

# Story

We are building an interactive analytics dashboard to help LifeFlight understand its historical operations and forecast emergency medical demand. The dashboard will also let users compare different resource allocation scenarios, like testing different base locations and service coverage areas.

Our prototype focuses on three main areas:
- Visualizing current mission volume, response times, and base workload
- Using Prophet time-series model with demographic data to forecast future mission demand
- Providing interactive maps to compare service coverage under different base configurations

This is a prototype and decision support tool that LifeFlight staff can use and build on for future work, not a production-ready optimization system.

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
## Description
We use **LifeFlight operational data** as our primary dataset (transport volume, pickup locations, bases, and asset types). We also use external data sources:

- **Population and demographic data** - historical and projected data at county/city level
- **Age structure variables** - used as external regressors in our forecasting model
- **Weather history data** - explored for potential future use

Right now, demographic variables are integrated into the forecasting model. Weather data is documented but not yet implemented.

## Source & Risks
The main challenge is cleaning and aligning multiple external datasets (population, demographics, weather) within our limited timeframe. Integrating them into robust long-term forecasting is complex.

---

# Scope & Objectives

## What We Built

### 1. Current Operations & Service Quality Analysis

We analyze LifeFlight's current performance through several metrics:
- Mission volume patterns by weekday and hour
- Dispatch and response time distribution
- Base workload comparison (air and ground units)
- "Transport by Primary Q" analysis - whether patients got the right asset without delay
- Expected completion rate and reasons when bases don't respond

### 2. Demand Forecasting

We built a multi-year forecasting system:
- Prophet time-series model with demographic/age-structure data as regressors
- Model performance metrics (MAE, MAPE, RMSE)
- Seasonality analysis using weekday/hour heatmaps


### 3. Base Layout Scenario Simulation

Users can test different base configurations:
- Interactive map with existing and potential new base locations
- Adjustable service radius for different scenarios
- Response time analysis by city and base
- Ground-unit specific coverage analysis (like neoGround)

## Technical Stack

- **Backend:** Flask REST API for data processing and forecasts
- **Frontend:** Observable Framework for interactive dashboard
- **Deployment:** GitHub Pages (static build in `docs/`)

---

# Visualization Plan

We have **3 main categories with 10+ visualizations** in the working prototype.

## 1) Current Operations & Service Quality Dashboard

**1.1 Mission Volume Distribution (Heatmap)**
- Shows when missions happen most (weekday × hour)
- Helps identify peak demand periods

**1.2 Response Time Analysis (Line Chart)**
- Average response time (dispatch to enroute) by hour
- Shows patterns throughout the day for current month

**1.3 Base Workload Analysis (Bar/Area Charts)**
- Compares workload across different bases
- Separate views for air units and ground units

**1.4 Transport by Primary Q Analysis**
- **Delay Rate Chart:** Shows proportion of "Yes" responses by base (whether patient got appropriate asset without delay)
- **Delay Reason Chart:** Shows why delays happened when conditions weren't met

**1.5 Expected Completion Rate & No Response Reasons**
- **Completion Rate Chart:** Compares `appropriateAsset` vs `respondingAssets` by base
- **No Response Reasons Chart:** Shows why expected bases didn't respond

---

## 2) Demand Forecasting

**2.1 Multi-year Demand Forecast (Line Chart)**
- Prophet model forecast with confidence intervals
- Uses age-structure variables from population data
- Shows historical data and future projections
- Reports MAE, MAPE, RMSE for evaluation

**2.2 Seasonality Heatmap**
- Long-term demand patterns by weekday and hour
- Shows cyclical patterns in historical data

---

## 3) Scenario Modeling & Base Layout

**3.1 Interactive Coverage Map**
- Toggle existing and candidate base locations
- Adjust service radius to compare scenarios
- Real-time coverage visualization
- Compare different base configurations

**3.2 Response Time by City**
- City-level response time analysis by base
- Identifies locations with longer response times
- Helps find underserved areas

**3.3 Ground Unit Coverage (neoGround Analysis)**
- Ground-unit specific analysis
- Estimates typical speeds and coverage radius
- Shows compliance rates for ground transport

---

# KPIs & Success Metrics

Our dashboard currently tracks:
- Mission volume (overall and by time periods)
- Base workload distribution
- Dispatch and response time metrics
- Completion rate (missions handled by expected base)
- Coverage and compliance in scenario simulations

We documented additional KPIs (unit cost, fleet utilization, safety incidents) as potential future extensions, but they're not in this version.

---

# Summary

**Current Operations Dashboard:** 5+ charts  
**Demand Forecasting:** 2 charts  
**Scenario Modeling:** 3+ interactive visualizations  
**Total: 10+ core visualizations** implemented and working

---