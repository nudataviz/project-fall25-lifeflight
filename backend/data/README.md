# Data Directory

## Overview

This directory contains all data files organized by functional area for the LifeFlight FlightPath Optimizer project.

## Directory Structure

- `1_demand_forecasting/` - Data for demand forecasting models
- `2_scenario_modeling/` - Data for scenario modeling
- `3_resource_optimization/` - Data for resource optimization
- `4_kpi_dashboard/` - Data for KPI dashboard
- `raw/` - Original raw data files
- `reference/` - Documentation and reference files

## Documentation

- `DATA_STATUS.md` - Data readiness status (data required for four sections and their readiness)
- `DATA_DOCUMENTATION.md` - Detailed data documentation

## Team Contributions

### Shenyu Li (Team Lead)
- Wrote second version of proposal and EDA, collected weather data (1997-2025) and demographic data
- Developed data preprocessing utilities (`utils/data_processing.py`) and organized data into four functional modules
- Generated age structure data (2010-2026) and county population data (2020-2024) from screenshots with interpolation
- Created comprehensive data documentation (`DATA_STATUS.md`, `DATA_DOCUMENTATION.md`) and updated all README files to English
- Built data processing pipeline (`process_data.py`) with all processed data saved to `processed/` directory

### Yantong Guo
- Wrote first version of proposal and EDA
- Collected operational data (FlightTransportsMaster, Oasis, Roux) and conducted preliminary investigation
- Developed `model.ipynb` for predictive modeling
- Established backend framework and created `eda.ipynb`
- Built first version of website with three visualizations

## Visualization Results

*[Screenshots and visualization results will be added here]*
