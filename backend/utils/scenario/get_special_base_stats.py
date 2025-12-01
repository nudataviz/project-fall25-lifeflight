"""
Calculate statistics for special bases (B-CCT, L-CCT, S-CCT, neoGround).
"""
import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional, Any
# from geopy.distance import geodesic  # Using haversine_distance instead
from utils.getData import read_data
from utils.scenario.get_time_diff import get_time_diff_seconds, clean_time
from utils.heatmap import get_city_coordinates
from utils.scenario.get_range_map import (
    haversine_distance,
    calculate_coverage_stats,
    calculate_response_time_and_distance,
    calculate_compliance_rate
)


def calculate_special_base_speeds() -> Dict[str, float]:
    """
    Calculate median speed for each special base (B-CCT, L-CCT, S-CCT, neoGround).
    
    Returns:
        Dict mapping base name to median speed (miles per hour)
    """
    # Load data
    df = read_data('FlightTransportsMaster.csv')
    df = df[df['PU State'] == 'Maine']
    
    # Fix column name (remove trailing space)
    if 'TASC Primary Asset ' in df.columns:
        df.rename(columns={'TASC Primary Asset ': 'TASC Primary Asset'}, inplace=True)
    
    # Filter for special bases only
    special_bases = ['neoGround', 'L-CCT', 'B-CCT', 'S-CCT']
    df = df[df['TASC Primary Asset'].isin(special_bases)]
    df = df[df['TASC Primary Asset'].notna()]
    
    # Map base to its main city
    base_city = {}
    for center in special_bases:
        city_counts = df[df['TASC Primary Asset'] == center]['PU City'].value_counts(ascending=False)
        if len(city_counts) > 0:
            base_city[center] = city_counts.index[0]
    
    # Add base city to dataframe
    df['base_city'] = df['TASC Primary Asset'].map(base_city)
    
    # Get city coordinates
    city_coordinates = get_city_coordinates(isOnlyMaine=True)
    
    # Add coordinates
    df['base_city_coord'] = df['base_city'].map(city_coordinates)
    df['PU City_coord'] = df['PU City'].map(city_coordinates)
    
    # Remove rows without coordinates
    df = df[df['base_city_coord'].notna() & df['PU City_coord'].notna()].copy()
    
    # Calculate distance using haversine
    from utils.scenario.get_range_map import haversine_distance
    
    def calculate_distance(row):
        base_coord = row['base_city_coord']
        pu_coord = row['PU City_coord']
        if base_coord is None or pu_coord is None:
            return None
        if isinstance(base_coord, (list, tuple)) and len(base_coord) >= 2:
            base_lat, base_lon = base_coord[0], base_coord[1]
        else:
            return None
        if isinstance(pu_coord, (list, tuple)) and len(pu_coord) >= 2:
            pu_lat, pu_lon = pu_coord[0], pu_coord[1]
        else:
            return None
        return haversine_distance(base_lat, base_lon, pu_lat, pu_lon)
    
    df['distance'] = df.apply(calculate_distance, axis=1)
    
    # Calculate time difference
    df['time_diff_seconds'] = get_time_diff_seconds(df, 'enrtime', 'atstime')
    df['time_diff_hours'] = df['time_diff_seconds'] / 3600
    
    # Clean data
    df = df[df['time_diff_hours'] > 0]
    df = df[df['distance'].notna() & (df['distance'] > 0)]
    
    # Calculate speed (miles per hour)
    df['speed'] = df['distance'] / df['time_diff_hours']
    
    # Remove unreasonable speeds (e.g., > 1000 mph)
    df = df[df['speed'] < 1000]
    
    # Calculate median speed for each base
    speed_stats = df.groupby('TASC Primary Asset')['speed'].median().to_dict()
    
    return speed_stats


def get_special_base_data(center_type: str) -> pd.DataFrame:
    """
    Get and process data for a specific center type.
    
    Args:
        center_type: One of 'neoGround', 'L-CCT', 'B-CCT', 'S-CCT'
        
    Returns:
        Processed DataFrame with speed calculations
    """
    # Load data
    df = read_data('FlightTransportsMaster.csv')
    df = df[df['PU State'] == 'Maine']
    
    # Fix column name
    if 'TASC Primary Asset ' in df.columns:
        df.rename(columns={'TASC Primary Asset ': 'TASC Primary Asset'}, inplace=True)
    
    # Filter for specific center
    df = df[df['TASC Primary Asset'] == center_type]
    df = df[df['TASC Primary Asset'].notna()]
    
    # Map base to its main city
    city_counts = df['PU City'].value_counts(ascending=False)
    if len(city_counts) > 0:
        base_city = city_counts.index[0]
        df['base_city'] = base_city
    else:
        return pd.DataFrame()
    
    # Get city coordinates
    city_coordinates = get_city_coordinates(isOnlyMaine=True)
    
    # Add coordinates
    df['base_city_coord'] = df['base_city'].map(city_coordinates)
    df['PU City_coord'] = df['PU City'].map(city_coordinates)
    
    # Remove rows without coordinates
    df = df[df['base_city_coord'].notna() & df['PU City_coord'].notna()].copy()
    
    # Calculate distance using haversine
    from utils.scenario.get_range_map import haversine_distance
    
    def calculate_distance(row):
        base_coord = row['base_city_coord']
        pu_coord = row['PU City_coord']
        if base_coord is None or pu_coord is None:
            return None
        if isinstance(base_coord, (list, tuple)) and len(base_coord) >= 2:
            base_lat, base_lon = base_coord[0], base_coord[1]
        else:
            return None
        if isinstance(pu_coord, (list, tuple)) and len(pu_coord) >= 2:
            pu_lat, pu_lon = pu_coord[0], pu_coord[1]
        else:
            return None
        return haversine_distance(base_lat, base_lon, pu_lat, pu_lon)
    
    df['distance'] = df.apply(calculate_distance, axis=1)
    
    # Calculate time difference
    df['time_diff_seconds'] = get_time_diff_seconds(df, 'enrtime', 'atstime')
    df['time_diff_minutes'] = df['time_diff_seconds'] / 60
    df['time_diff_hours'] = df['time_diff_seconds'] / 3600
    
    # Clean data
    df = clean_time(df, 'time_diff_minutes')
    df = df[(df['time_diff_minutes'] > 0) & (df['time_diff_minutes'] < 400)]
    df = df[df['distance'].notna() & (df['distance'] > 0)]
    df = df[df['time_diff_hours'] > 0]
    
    # Calculate speed
    df['speed'] = df['distance'] / df['time_diff_hours']
    df = df[df['speed'] < 1000]
    
    return df


def calculate_special_base_statistics(
    center_type: str,
    radius_miles: float,
    expected_time: float,
    base_cities_list: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate statistics for a special base.
    
    Args:
        center_type: One of 'neoGround', 'L-CCT', 'B-CCT', 'S-CCT'
        radius_miles: Service radius in miles
        expected_time: Expected response time in minutes
        base_cities_list: Optional list of base city names (for what-if scenario)
        
    Returns:
        Dict with coverage stats, compliance stats, speed stats, and processed data
    """
    # Get base city for the center
    df = read_data('FlightTransportsMaster.csv')
    df = df[df['PU State'] == 'Maine']
    
    if 'TASC Primary Asset ' in df.columns:
        df.rename(columns={'TASC Primary Asset ': 'TASC Primary Asset'}, inplace=True)
    
    df_center = df[df['TASC Primary Asset'] == center_type]
    if len(df_center) == 0:
        return {
            'coverage_stats': {},
            'compliance_stats': {'total_tasks': 0, 'compliant_tasks': 0, 'compliance_rate': 0.0, 'avg_response_time': 0.0},
            'speed_stats': {},
            'processed_data': []
        }
    
    # Find main base city
    city_counts = df_center['PU City'].value_counts(ascending=False)
    main_base_city = city_counts.index[0] if len(city_counts) > 0 else None
    
    # Get coordinates
    city_coords = get_city_coordinates(isOnlyMaine=True)
    
    # Determine which cities to use
    if base_cities_list:
        # Normalize city names: uppercase and strip spaces
        base_cities_list = [city.upper().strip() if isinstance(city, str) else str(city).upper().strip() 
                           for city in base_cities_list]
        # Filter to only valid cities
        base_cities_list = [city for city in base_cities_list if city in city_coords]
    else:
        base_cities_list = [main_base_city] if main_base_city and main_base_city in city_coords else []
    
    if not base_cities_list:
        return {
            'coverage_stats': {},
            'compliance_stats': {'total_tasks': 0, 'compliant_tasks': 0, 'compliance_rate': 0.0, 'avg_response_time': 0.0},
            'speed_stats': {},
            'processed_data': []
        }
    
    # Create base locations list
    base_locations = []
    for base_city in base_cities_list:
        if base_city in city_coords:
            base_locations.append({
                'name': base_city,
                'latitude': city_coords[base_city][0],
                'longitude': city_coords[base_city][1]
            })
    
    if not base_locations:
        return {
            'coverage_stats': {},
            'compliance_stats': {'total_tasks': 0, 'compliant_tasks': 0, 'compliance_rate': 0.0, 'avg_response_time': 0.0},
            'speed_stats': {},
            'processed_data': []
        }
    
    # 1. Calculate coverage stats for all bases
    coverage_stats = calculate_coverage_stats(
        base_locations, 
        radius_miles, 
        city_coords
    )
    
    # 2. Get processed data for this center
    df_processed = get_special_base_data(center_type)
    
    if len(df_processed) == 0:
        return {
            'coverage_stats': coverage_stats,
            'compliance_stats': {'total_tasks': 0, 'compliant_tasks': 0, 'compliance_rate': 0.0, 'avg_response_time': 0.0},
            'speed_stats': {},
            'processed_data': []
        }
    
    # Calculate median speed
    median_speed = df_processed['speed'].median()
    if pd.isna(median_speed) or median_speed <= 0:
        median_speed = 0.0
    speed_stats = {
        'median_speed_mph': round(float(median_speed), 2)
    }
    
    # 3. Calculate response time and distance for tasks within radius
    # Filter tasks within radius
    df_processed['pickup_lat'] = df_processed['PU City'].apply(
        lambda x: city_coords.get(x, (None, None))[0] if x in city_coords else None
    )
    df_processed['pickup_lon'] = df_processed['PU City'].apply(
        lambda x: city_coords.get(x, (None, None))[1] if x in city_coords else None
    )
    
    df_processed = df_processed[df_processed['pickup_lat'].notna() & df_processed['pickup_lon'].notna()].copy()
    
    if len(df_processed) == 0:
        return {
            'coverage_stats': coverage_stats,
            'compliance_stats': {'total_tasks': 0, 'compliant_tasks': 0, 'compliance_rate': 0.0, 'avg_response_time': 0.0},
            'speed_stats': speed_stats,
            'processed_data': []
        }
    
    # Calculate distance from each base to pickup city, find nearest base within radius
    def assign_nearest_base(row):
        pickup_lat = row['pickup_lat']
        pickup_lon = row['pickup_lon']
        
        min_distance = float('inf')
        assigned_base = None
        
        for base in base_locations:
            distance = haversine_distance(
                base['latitude'],
                base['longitude'],
                pickup_lat,
                pickup_lon
            )
            if distance <= radius_miles and distance < min_distance:
                min_distance = distance
                assigned_base = base['name']
        
        return pd.Series({
            'pickup_distance_miles': min_distance if assigned_base else None,
            'assigned_base': assigned_base
        })
    
    distance_info = df_processed.apply(assign_nearest_base, axis=1)
    df_processed['pickup_distance_miles'] = distance_info['pickup_distance_miles']
    df_processed['assigned_base'] = distance_info['assigned_base']
    
    # Filter tasks within radius (assigned to at least one base)
    df_within_radius = df_processed[df_processed['assigned_base'].notna()].copy()
    
    # If new base cities are provided, estimate response time using median speed
    if base_cities_list and len(df_within_radius) > 0 and median_speed > 0:
        # Estimate response time = distance / speed (in hours, then convert to minutes)
        df_within_radius['estimated_time_minutes'] = (
            df_within_radius['pickup_distance_miles'] / median_speed * 60
        ).round(3)
        # Use estimated time for compliance calculation
        df_within_radius['time_diff_minutes'] = df_within_radius['estimated_time_minutes']
    
    # 4. Calculate compliance rate
    compliance_stats = calculate_compliance_rate(df_within_radius, expected_time)
    
    # Prepare processed data for frontend
    processed_data = []
    if len(df_processed) > 0:
        cols_to_include = [
            'PU City', 'TASC Primary Asset', 
            'time_diff_minutes', 'distance', 'speed',
            'pickup_distance_miles'
        ]
        available_cols = [col for col in cols_to_include if col in df_processed.columns]
        processed_data = df_processed[available_cols].to_dict(orient='records')
        
        # Replace NaN with None for JSON serialization
        for record in processed_data:
            for key, value in record.items():
                if pd.isna(value) or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
                    record[key] = None
                elif isinstance(value, (np.integer, np.floating)):
                    record[key] = float(value)
    
    return {
        'coverage_stats': coverage_stats,
        'compliance_stats': compliance_stats,
        'speed_stats': speed_stats,
        'processed_data': processed_data
    }

