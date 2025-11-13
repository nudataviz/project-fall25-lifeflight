# Data Status

## 1. Demand Forecasting

### Required Data:
- ✅ Operational data (2012-2023, 18,382 records) - **Ready**
- ✅ Weather data (1997-2025, merged) - **Ready**
- ✅ Population data (2012-2023, state-level) - **Ready**
- ✅ Population projections (2024-2042) - **Ready (CSV files parsed)**
  - **Files**: `MaineStateCountyPopulationProjections2042.csv`, `MaineCityTownPopulationProjection2042.csv`
- ✅ Age structure data (2010-2026, county-level 65+ share) - **Ready (complete)**
  - **Data source**: 2010-2015 actual data + 2016, 2021, 2026 estimated from screenshots + other years linearly interpolated
  - **File**: `processed/age_structure_2010_2026.csv` (272 rows, 17 years × 16 counties)
  - **Note**: 2016-2023 complete (128 rows), 2017-2020, 2022-2023 linearly interpolated
- ✅ County population data (2020-2024) - **Ready**
  - **File**: `processed/county_population_2020_2024.csv` (80 rows, 5 years × 16 counties)
- ✅ Hospital facility closures (2015-2024) - **Ready (CSV file created)**
  - **File**: `hospital_facility_closures.csv`
  - **Data**: 11 birthing units closed, 26 nursing homes closed
  - **Source**: Maine Monitor news article

## 2. Scenario Modeling

### Required Data:
- ✅ Operational data (2012-2023) - **Ready**
- ✅ Geographic data (city coordinates) - **Ready**
- ✅ Population data (2012-2023) - **Ready**
- ✅ City-county mapping (348 cities, 16 counties) - **Ready**
- ✅ Weather data (1997-2025) - **Ready**

## 3. Resource Optimization

### Required Data:
- ✅ Operational data (2012-2023) - **Ready**
- ✅ Detailed operational data (Oasis.csv, FlightTransportsMaster.csv) - **Ready**
- ✅ Vehicle and crew data - **Ready**

## 4. KPI Dashboard

### Required Data:
- ✅ Operational data (2012-2023) - **Ready**
- ✅ Weather data (merged) - **Ready**
- ✅ Time series data - **Ready**

## Summary

### ✅ Ready (100%)
- Operational data (2012-2023, 18,382 records)
- Weather data (1997-2025, merged)
- Population data (2012-2023, state-level)
- County population data (2020-2024)
- Population projections (2024-2042) - **CSV files parsed**
- Historical city/town population data (2010-2020) - **CSV files parsed**
- Age structure data (2010-2026, complete)
- City-county mapping (348 cities, 16 counties)
- Geographic data (city coordinates)

### ✅ Ready (From News Article)
- Hospital facility closures (2015-2024)
  - **File**: `hospital_facility_closures.csv`
  - **Data**: Birthing unit closures (11 closed, 17 remaining) and nursing home closures (26 closed, 78 remaining)
  - **Source**: Maine Monitor news article
  - **Note**: Includes specific closures and county-level statistics

## Data Files Location

### Processed Data (`processed/`)
- `population_parsed.csv` - Population data (2012-2023, 12 rows)
- `county_population_2020_2024.csv` - County population data (2020-2024, 80 rows, 5 years × 16 counties)
- `age_structure_processed.csv` - Age structure (2010-2015, 96 rows, 16 counties)
- `age_structure_2010_2026.csv` - Age structure (2010-2026, 272 rows, 17 years × 16 counties) - **Complete data with interpolation**
- `city_county_mapping.csv` - City-county mapping (348 cities, 16 counties)
- `operational_with_weather.csv` - Operational data with weather (18,382 rows)

### Parsed CSV Files (`1_demand_forecasting/`)
- `MaineStateCountyPopulationProjections2042.csv` - County population projections (to 2042)
- `MaineCityTownPopulationProjection2042.csv` - City/town population projections (to 2042)
- `Total Population for Maine Cities and Towns (2010-2019).csv` - Historical city/town population (2010-2019)
- `Total Population_2020_3.csv` - 2020 city/town population
- `hospital_facility_closures.csv` - Hospital facility closures (2015-2024)
  - Birthing unit closures: 11 closed, 17 remaining
  - Nursing home closures: 26 closed, 78 remaining

### Original Excel Files (Optional) (`1_demand_forecasting/`)
- `MaineStateCountyPopulationProjections2042.xlsx` - Original Excel file (parsed to CSV)
- `MaineCityTownPopulationProjection2042.xlsx` - Original Excel file (parsed to CSV)
- `Total Population for Maine Cities and Towns (2010-2019).xlsx` - Original Excel file (parsed to CSV)
- `Total Population_2020_3.xlsx` - Original Excel file (parsed to CSV)
