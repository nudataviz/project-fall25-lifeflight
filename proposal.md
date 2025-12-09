# ProjectName
FlightPath Dashboard

# Story

We are building an interactive analytics dashboard to help LifeFlight explore its historical operations, forecast emergency medical demand over multiple years, and compare different resource allocation scenarios (like different base locations and service coverage areas).

The prototype focuses on:
- Visualizing current mission volume, response times, and base workload
- Using Prophet time-series model with demographic variables to forecast future mission demand
- Providing interactive maps to compare service coverage and response times under different base layouts

The goal is to offer a transparent, data-driven decision support tool that LifeFlight staff can build on in future work, not a production optimization engine.

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
We primarily use historical and current **LifeFlight operational data** (transport volume, pickup locations, bases, and asset types) and supplement it with external data:

- **Population and demographic data** - historical and projections at county/city level
- **Age structure variables** - used as external regressors in the forecasting model
- **Public weather history sources** - explored as potential future regressors

In the current prototype, demographic variables are integrated into the forecasting model. Weather data is documented as a possible extension but not yet fully incorporated.

## Source / Risks
The main challenge is the complexity of cleaning and aligning multiple external datasets (population, demographics, weather) and the limited time to fully integrate them into robust long-term forecasting and scenario simulations.

---

# Scope & Objectives

## What We've Built

### 1. Current Operations & Service Quality Analysis

- Mission volume by weekday and hour
- Dispatch/response time distribution
- Base workload comparison across air and ground units
- "Transport by Primary Q" analysis (whether patients get appropriate asset without delay)
- Expected completion rate and no-response reason analysis

### 2. Mid- to Long-Term Demand Forecasting

- Multi-year mission volume forecasting using Prophet time-series model
- External regressors based on demographic and age-structure data
- Model performance metrics (MAE, MAPE, RMSE)
- Seasonality analysis via weekday/hour heatmaps


### 3. Scenario Simulation of Base Layout and Service Scope

- Interactive coverage map with existing and candidate base locations
- Adjustable service radius for scenario comparison
- Response time analysis by city and base
- Ground-unit-specific coverage analysis (e.g., neoGround)

## Technical Stack

- **Backend:** Flask REST API providing processed data and forecast endpoints
- **Frontend:** Observable Framework interactive dashboard
- **Deployment:** GitHub Pages (static build served from `docs/`)

---

# Visualization Plan
**Total: 3 categories, 10+ core visualizations** in the working prototype.

## 1) Current Operations & Service Quality Dashboard

**1.1 Mission Volume Distribution (Weekday × Hour Heatmap)**
- Aggregates historical missions by weekday and hour to find peak demand periods
- Heatmap showing mission volume patterns across time

**1.2 Response Time Analysis (Hourly Distribution)**
- Shows average response time (dispatch time - enroute time) by hour of day for current month
- Line chart showing response time patterns throughout the day

**1.3 Base Workload Analysis**
- Compares workload across different bases (air units and ground units)
- Bar/area charts showing workload distribution by base

**1.4 Transport by Primary Q Analysis**
- Analyzes the `transportByPrimaryQ` field to measure whether patients were transported by the most appropriate asset without delay
- Two charts:
  - Delay Rate: proportion of "Yes" responses by base
  - Delay Reason: causes of delays when conditions are not met

**1.5 Expected Completion Rate & No Response Reasons**
- Evaluates whether tasks were completed by the expected base (`appropriateAsset` vs `respondingAssets`)
- Two charts:
  - Expected Completion Rate by Base
  - No Response Reasons by Base (why expected bases did not respond)

---

## 2) Demand Forecasting

**2.1 Multi-year Demand Forecast**
- Uses Prophet time-series model with demographic regressors to forecast mission volume
- Integrates age-structure variables derived from population data
- Reports MAE, MAPE, and RMSE for model evaluation
- Line chart with historical and forecasted mission volume, including confidence intervals

**2.2 Seasonality & Day-of-Week/Hour Heatmap**
- Aggregates historical missions by weekday and hour to show cyclical patterns
- Heatmap showing long-term demand patterns across time

---

## 3) Scenario Modeling & Base Layout

**3.1 Interactive Coverage Map**
- Interactive map allowing users to toggle existing and candidate base locations and adjust service radius for scenario comparison
- Features include:
  - Real-time coverage visualization
  - Comparison of coverage under different base configurations
- Interactive map with coverage areas and base location markers

**3.2 Response Time by City**
- Analyzes city-level response times by base to identify locations with significantly longer response times
- Chart/map showing response time patterns across different cities and bases

**3.3 Ground Unit Service Coverage**
- Ground-unit-specific analysis estimating typical speeds, coverage radius, and compliance rates for units like neoGround
- Coverage map and metrics specific to ground transport units


---

# KPIs & Success Metrics

In the current prototype, the dashboard focuses on:

- Mission volume (overall and by time of week)
- Base workload distribution
- Dispatch/response time metrics
- Proportion of missions completed by the expected base
- Coverage and compliance metrics in scenario simulations

Additional KPIs like unit cost, fleet utilization, or safety incident rates are documented as potential extensions but are not implemented in this version.

---

# Summary
- **Current Operations & Service Quality Dashboard:** 5+ charts
- **Demand Forecasting:** 2 charts
- **Scenario Modeling & Base Layout:** 3+ interactive visualizations

**Total: 10+ core visualizations** implemented and working

---