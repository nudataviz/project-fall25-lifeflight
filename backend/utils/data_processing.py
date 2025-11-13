"""
Data processing utilities for LifeFlight FlightPath Optimizer project.

This module provides functions to parse and process various data files:
- Parse population_data.csv (JSON format)
- Process age structure data (calculate 65+ population share)
- Create city-to-county mapping table
- Integrate weather data with operational data
"""

import pandas as pd
import json
import ast
import os
from typing import Dict, Tuple, Optional
from datetime import datetime


def parse_population_data(file_path: str) -> pd.DataFrame:
    """
    Parse population_data.csv which contains JSON strings.
    
    Args:
        file_path: Path to population_data.csv
        
    Returns:
        DataFrame with columns: year, population
    """
    df = pd.read_csv(file_path)
    
    # Parse JSON strings and extract population numbers
    populations = []
    for idx, row in df.iterrows():
        try:
            # Parse the JSON-like string
            data_str = row['population']
            # Remove quotes and parse as Python list
            data = ast.literal_eval(data_str)
            # Extract population from the nested list structure
            # Format: [['NAME', 'B01003_001E', 'state'], ['Maine', '1329192', '23']]
            if len(data) > 1 and len(data[1]) > 1:
                population = int(data[1][1])  # Extract population number
                populations.append(population)
            else:
                populations.append(None)
        except (ValueError, IndexError, SyntaxError) as e:
            print(f"Error parsing row {idx}: {e}")
            populations.append(None)
    
    # Create cleaned DataFrame
    result_df = pd.DataFrame({
        'year': df['year'].values,
        'population': populations
    })
    
    # Sort by year
    result_df = result_df.sort_values('year').reset_index(drop=True)
    
    return result_df


def process_age_structure(file_path: str, output_path: Optional[str] = None) -> pd.DataFrame:
    """
    Process age structure data to calculate 65+ population share by county.
    
    Census data YEAR mapping (typical):
    - YEAR 1 = April 2010 (base estimate)
    - YEAR 2 = July 2010
    - YEAR 3 = July 2011
    - YEAR 4 = July 2012
    - YEAR 5 = July 2013
    - YEAR 6 = July 2014
    
    For this dataset, we'll map YEAR to approximate years:
    - YEAR 1 = 2010
    - YEAR 2 = 2011
    - YEAR 3 = 2012
    - YEAR 4 = 2013
    - YEAR 5 = 2014
    - YEAR 6 = 2015
    
    Args:
        file_path: Path to cc-est2024-syasex-23.csv
        output_path: Optional path to save processed data
        
    Returns:
        DataFrame with columns: county, year, total_population, population_65plus, pct_65plus
    """
    df = pd.read_csv(file_path)
    
    # Filter for county-level data (SUMLEV == 50)
    county_df = df[df['SUMLEV'] == 50].copy()
    
    # YEAR mapping: YEAR 1 = 2010, YEAR 2 = 2011, etc.
    # For estimates, typically YEAR 1 = base year (2010), YEAR 2 = 2011, etc.
    year_mapping = {1: 2010, 2: 2011, 3: 2012, 4: 2013, 5: 2014, 6: 2015}
    
    # Group by county and year
    county_year_groups = []
    
    for (county_name, year_code), group in county_df.groupby(['CTYNAME', 'YEAR']):
        # Calculate total population (sum all ages)
        # Note: AGE 85 typically represents 85+ (all ages 85 and older)
        total_pop = group['TOT_POP'].sum()
        
        # Calculate 65+ population
        # AGE represents single years (0, 1, 2, ..., 84) and 85+ (AGE 85)
        # So AGE >= 65 includes ages 65-84 and 85+
        population_65plus = group[group['AGE'] >= 65]['TOT_POP'].sum()
        
        pct_65plus = (population_65plus / total_pop * 100) if total_pop > 0 else 0
        
        # Map YEAR code to actual year
        actual_year = year_mapping.get(year_code, None)
        if actual_year is None:
            # If YEAR code not in mapping, skip or use a default
            continue
        
        county_year_groups.append({
            'county': county_name.replace(' County', '').strip(),  # Remove " County" suffix
            'year': actual_year,
            'total_population': int(total_pop),
            'population_65plus': int(population_65plus),
            'pct_65plus': round(pct_65plus, 2)
        })
    
    result_df = pd.DataFrame(county_year_groups)
    result_df = result_df.sort_values(['county', 'year']).reset_index(drop=True)
    
    if output_path:
        result_df.to_csv(output_path, index=False)
        print(f"Processed age structure data saved to {output_path}")
    
    return result_df


def create_city_county_mapping(
    operational_data_path: str,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Create city-to-county mapping table from operational data.
    
    The data.csv file has TWO PU City columns:
    - First PU City (column 13): Actual city name (e.g., MACHIAS, FORT KENT)
    - Second PU City (column 18, named 'PU City.1'): County name (e.g., Washington, Aroostook)
    - PU State (column 19): State name (e.g., Maine, New Hampshire)
    
    Args:
        operational_data_path: Path to data.csv
        output_path: Optional path to save mapping table
        
    Returns:
        DataFrame with columns: city, county, state
    """
    df = pd.read_csv(operational_data_path, encoding='latin1')
    
    # Extract unique city-county-state pairs
    # Use first PU City as city name, second PU City (PU City.1) as county name
    if 'PU City.1' in df.columns:
        city_county_pairs = df[['PU City', 'PU City.1', 'PU State']].drop_duplicates()
        city_county_pairs = city_county_pairs[city_county_pairs['PU City'].notna()]
        city_county_pairs = city_county_pairs[city_county_pairs['PU City.1'].notna()]
        city_county_pairs = city_county_pairs[city_county_pairs['PU State'].notna()]
        
        # Rename columns
        city_county_pairs.columns = ['city', 'county', 'state']
    else:
        # Fallback: if PU City.1 doesn't exist, use PU State as county
        # (Some versions might have different column names)
        city_county_pairs = df[['PU City', 'PU State']].drop_duplicates()
        city_county_pairs = city_county_pairs[city_county_pairs['PU City'].notna()]
        city_county_pairs = city_county_pairs[city_county_pairs['PU State'].notna()]
        city_county_pairs.columns = ['city', 'county', 'state']
        city_county_pairs['state'] = 'Maine'  # Default to Maine
    
    # Clean data
    city_county_pairs['city'] = city_county_pairs['city'].str.strip().str.upper()
    city_county_pairs['county'] = city_county_pairs['county'].str.strip().str.upper()
    city_county_pairs['state'] = city_county_pairs['state'].str.strip()
    
    # Define Maine counties (official list)
    maine_counties = [
        'ANDROSCOGGIN', 'AROOSTOOK', 'CUMBERLAND', 'FRANKLIN', 'HANCOCK',
        'KENNEBEC', 'KNOX', 'LINCOLN', 'OXFORD', 'PENOBSCOT', 'PISCATAQUIS',
        'SAGADAHOC', 'SOMERSET', 'WALDO', 'WASHINGTON', 'YORK'
    ]
    
    # Filter for valid Maine counties
    city_county_pairs = city_county_pairs[
        city_county_pairs['county'].isin(maine_counties)
    ]
    
    # For cities with multiple counties, keep the most common one
    # Count occurrences of each city-county pair
    city_county_counts = city_county_pairs.groupby(['city', 'county']).size().reset_index(name='count')
    
    # For each city, keep the county with the highest count
    city_county_map = city_county_counts.sort_values(['city', 'count'], ascending=[True, False])
    city_county_map = city_county_map.drop_duplicates(subset=['city'], keep='first')
    
    # Merge back with state information
    result_df = city_county_map[['city', 'county']].merge(
        city_county_pairs[['city', 'state']].drop_duplicates(),
        on='city',
        how='left'
    )
    
    # Fill missing states with Maine
    result_df['state'] = result_df['state'].fillna('Maine')
    
    # Sort by city
    result_df = result_df.sort_values('city').reset_index(drop=True)
    
    if output_path:
        result_df.to_csv(output_path, index=False)
        print(f"City-county mapping saved to {output_path}")
        print(f"Total mappings: {len(result_df)}")
        print(f"Unique cities: {result_df['city'].nunique()}")
        print(f"Unique counties: {result_df['county'].nunique()}")
        print(f"Counties: {sorted(result_df['county'].unique())}")
    
    return result_df


def parse_weather_date(date_str: str) -> Tuple[int, int]:
    """
    Parse weather date string to year and month.
    
    Args:
        date_str: Date string like "August, 2025" or "July, 2024"
        
    Returns:
        Tuple of (year, month)
    """
    try:
        # Remove quotes if present
        date_str = date_str.strip('"')
        # Parse format: "Month, Year"
        parts = date_str.split(',')
        if len(parts) == 2:
            month_str = parts[0].strip()
            year = int(parts[1].strip())
            
            # Convert month name to number
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month = month_map.get(month_str, None)
            return (year, month)
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
    return (None, None)


def clean_numeric_value(value) -> Optional[float]:
    """
    Clean numeric values that may contain commas or be empty.
    
    Args:
        value: Value to clean
        
    Returns:
        Cleaned numeric value or None
    """
    if pd.isna(value) or value == '':
        return None
    try:
        # Remove commas and convert to float
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return float(value)
    except (ValueError, TypeError):
        return None


def integrate_weather_data(
    operational_data_path: str,
    weather_data_path: str,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Integrate weather data with operational data by date.
    
    Args:
        operational_data_path: Path to data.csv
        weather_data_path: Path to maine_weather_1997_2025.csv
        output_path: Optional path to save integrated data
        
    Returns:
        DataFrame with operational data merged with weather data
    """
    # Load operational data
    operational_df = pd.read_csv(operational_data_path, encoding='latin1')
    operational_df['tdate'] = pd.to_datetime(operational_df['tdate'], errors='coerce')
    operational_df['year'] = operational_df['tdate'].dt.year
    operational_df['month'] = operational_df['tdate'].dt.month
    
    # Load weather data
    weather_df = pd.read_csv(weather_data_path)
    
    # Parse dates and clean numeric values
    weather_data = []
    for idx, row in weather_df.iterrows():
        year, month = parse_weather_date(row['Month'])
        if year and month:
            weather_data.append({
                'year': year,
                'month': month,
                'avg_temp': clean_numeric_value(row['AvgTemp']),
                'min_temp': clean_numeric_value(row['MinTemp']),
                'max_temp': clean_numeric_value(row['MaxTemp']),
                'precip': clean_numeric_value(row['Precip']),
                'heating_degree_days': clean_numeric_value(row['HeatingDegreeDays']),
                'cooling_degree_days': clean_numeric_value(row['CoolingDegreeDays'])
            })
    
    weather_processed_df = pd.DataFrame(weather_data)
    
    # Merge operational data with weather data
    merged_df = operational_df.merge(
        weather_processed_df,
        on=['year', 'month'],
        how='left'
    )
    
    if output_path:
        merged_df.to_csv(output_path, index=False)
        print(f"Integrated data saved to {output_path}")
    
    return merged_df


def process_all_data(
    data_dir: str = 'data',
    output_dir: Optional[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Process all data files and return processed DataFrames.
    
    Args:
        data_dir: Base data directory path
        output_dir: Optional output directory for processed files
        
    Returns:
        Dictionary of processed DataFrames
    """
    if output_dir is None:
        output_dir = data_dir
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    # 1. Parse population data
    print("Processing population data...")
    population_df = parse_population_data(
        os.path.join(data_dir, '1_demand_forecasting', 'population_data.csv')
    )
    results['population'] = population_df
    population_df.to_csv(
        os.path.join(output_dir, 'population_parsed.csv'),
        index=False
    )
    
    # 2. Process age structure
    print("Processing age structure data...")
    age_structure_df = process_age_structure(
        os.path.join(data_dir, '1_demand_forecasting', 'cc-est2024-syasex-23.csv')
    )
    results['age_structure'] = age_structure_df
    age_structure_df.to_csv(
        os.path.join(output_dir, 'age_structure_processed.csv'),
        index=False
    )
    
    # 3. Create city-county mapping
    print("Creating city-county mapping...")
    city_county_map = create_city_county_mapping(
        os.path.join(data_dir, 'data.csv')
    )
    results['city_county_mapping'] = city_county_map
    city_county_map.to_csv(
        os.path.join(output_dir, 'city_county_mapping.csv'),
        index=False
    )
    
    # 4. Integrate weather data
    print("Integrating weather data...")
    operational_with_weather = integrate_weather_data(
        os.path.join(data_dir, 'data.csv'),
        os.path.join(data_dir, '1_demand_forecasting', 'maine_weather_1997_2025.csv')
    )
    results['operational_with_weather'] = operational_with_weather
    operational_with_weather.to_csv(
        os.path.join(output_dir, 'operational_with_weather.csv'),
        index=False
    )
    
    print("All data processing completed!")
    return results


if __name__ == '__main__':
    # Example usage
    import sys
    
    # Get data directory from command line or use default
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'data'
    
    # Process all data
    results = process_all_data(data_dir, output_dir)
    
    # Print summary
    print("\n=== Processing Summary ===")
    for key, df in results.items():
        print(f"{key}: {len(df)} rows")

