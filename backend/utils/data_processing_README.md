# Data Processing Utilities

## Overview

The `data_processing.py` module provides utilities to parse and process various data files for the LifeFlight FlightPath Optimizer project.

## Functions

### 1. `parse_population_data(file_path)`
Parses `population_data.csv` which contains JSON strings and extracts actual population numbers.

**Input:** Path to `population_data.csv`
**Output:** DataFrame with columns: `year`, `population`

**Example:**
```python
from utils.data_processing import parse_population_data

df = parse_population_data('data/1_demand_forecasting/population_data.csv')
print(df.head())
```

### 2. `process_age_structure(file_path, output_path=None)`
Processes age structure data to calculate 65+ population share by county.

**Input:** Path to `cc-est2024-syasex-23.csv`
**Output:** DataFrame with columns: `county`, `year`, `total_population`, `population_65plus`, `pct_65plus`

**Example:**
```python
from utils.data_processing import process_age_structure

df = process_age_structure('data/1_demand_forecasting/cc-est2024-syasex-23.csv')
print(df.head())
```

### 3. `create_city_county_mapping(operational_data_path, output_path=None)`
Creates city-to-county mapping table from operational data.

**Input:** Path to `data.csv`
**Output:** DataFrame with columns: `city`, `county`, `state`

**Example:**
```python
from utils.data_processing import create_city_county_mapping

df = create_city_county_mapping('data/data.csv')
print(df.head())
```

### 4. `integrate_weather_data(operational_data_path, weather_data_path, output_path=None)`
Integrates weather data with operational data by date.

**Input:** 
- Path to `data.csv`
- Path to `maine_weather_1997_2025.csv`

**Output:** DataFrame with operational data merged with weather data (columns: `avg_temp`, `min_temp`, `max_temp`, `precip`, `heating_degree_days`, `cooling_degree_days`)

**Example:**
```python
from utils.data_processing import integrate_weather_data

df = integrate_weather_data(
    'data/data.csv',
    'data/1_demand_forecasting/maine_weather_1997_2025.csv'
)
print(df[['tdate', 'avg_temp', 'precip']].head())
```

### 5. `process_all_data(data_dir, output_dir)`
Processes all data files and saves results to output directory.

**Input:**
- `data_dir`: Base data directory path
- `output_dir`: Output directory for processed files

**Output:** Dictionary of processed DataFrames

**Example:**
```python
from utils.data_processing import process_all_data

results = process_all_data('data', 'data/processed')
for key, df in results.items():
    print(f"{key}: {len(df)} rows")
```

## Command Line Usage

Run the processing script from the backend directory:

```bash
cd backend
python process_data.py [data_dir] [output_dir]
```

**Default:**
- `data_dir`: `data`
- `output_dir`: `data/processed`

## Output Files

After processing, the following files are created in the output directory:

1. **`population_parsed.csv`** - Parsed population data (year, population)
2. **`age_structure_processed.csv`** - Processed age structure data (county, year, total_population, population_65plus, pct_65plus)
3. **`city_county_mapping.csv`** - City to county mapping (city, county, state)
4. **`operational_with_weather.csv`** - Operational data merged with weather data

## Notes

- The `city_county_mapping.csv` may contain some inaccuracies due to data quality issues in the source data. Manual review may be needed.
- The age structure data uses YEAR codes (1-6) which map to years 2010-2015.
- Weather data is merged by year and month, so all records in the same month will have the same weather data.

