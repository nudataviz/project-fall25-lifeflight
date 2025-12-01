"""
Generate range map with heatmap and service radius circles.
"""
import folium
import json
import os
from folium.plugins import HeatMap
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from math import radians, sin, cos, sqrt, atan2
from utils.heatmap import get_city_coordinates, process_city_demand, map_to_html, create_heatmap
from utils.getData import read_data
from utils.scenario.get_time_diff import get_time_diff_seconds, clean_time


def get_base_coordinates(base_names: List[str]) -> List[Dict[str, Any]]:
    """
    Get coordinates for base locations.
    
    Args:
        base_names: List of base city names
        
    Returns:
        List of dicts with name, latitude, longitude
    """
    city_coords = get_city_coordinates(isOnlyMaine=True)
    
    base_locations = []
    for base_name in base_names:
        if base_name in city_coords:
            coords = city_coords[base_name]
            base_locations.append({
                'name': base_name,
                'latitude': coords[0],
                'longitude': coords[1]
            })
    
    return base_locations


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    Returns:
        Distance in miles
    """
    R = 3959  # Earth radius in miles
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def calculate_coverage_stats(
    base_locations: List[Dict[str, Any]],
    radius_miles: float,
    city_coords: Dict[str, Tuple[float, float]]
) -> Dict[str, int]:
    """
    Calculate number of cities covered by each base within radius.
    
    Returns:
        Dict mapping base name to number of covered cities
    """
    coverage_stats = {}
    
    for base in base_locations:
        covered_cities = set()
        base_lat = base['latitude']
        base_lon = base['longitude']
        
        for city_name, coords in city_coords.items():
            if coords[0] is None or coords[1] is None:
                continue
            distance = haversine_distance(base_lat, base_lon, coords[0], coords[1])
            if distance <= radius_miles:
                covered_cities.add(city_name)
        
        coverage_stats[base['name']] = len(covered_cities)
    
    return coverage_stats


def calculate_response_time_and_distance(
    df: pd.DataFrame,
    base_locations: List[Dict[str, Any]],
    radius_miles: float,
    city_coords: Dict[str, Tuple[float, float]]
) -> pd.DataFrame:
    """
    Calculate response time and distance for tasks within radius.
    For each task, calculate distance from each selected base to pickup city,
    and assign the task to the nearest base within radius.
    
    Returns:
        DataFrame with response_time_minutes, pickup_distance_miles, and assigned_base columns
    """
    # Calculate response time
    df['time_diff_seconds'] = get_time_diff_seconds(df, 'enrtime', 'atstime')
    df['time_diff_minutes'] = (df['time_diff_seconds'] / 60).round(3)
    
    # Clean data
    df = clean_time(df, 'time_diff_minutes')
    df = df[(df['time_diff_minutes'] > 0) & (df['time_diff_minutes'] < 400)]
    df = df[df['TASC Primary Asset '].notna()]
    
    # Add city coordinates to dataframe
    df['pickup_lat'] = df['PU City'].apply(
        lambda x: city_coords.get(x, (None, None))[0] if x in city_coords else None
    )
    df['pickup_lon'] = df['PU City'].apply(
        lambda x: city_coords.get(x, (None, None))[1] if x in city_coords else None
    )
    
    # Filter out rows without valid coordinates
    df = df[df['pickup_lat'].notna() & df['pickup_lon'].notna()].copy()
    
    # For each task, calculate distance to each base and find the nearest base within radius
    def assign_base_and_distance(row):
        pickup_lat = row['pickup_lat']
        pickup_lon = row['pickup_lon']
        
        min_distance = float('inf')
        assigned_base = None
        
        for base in base_locations:
            distance = haversine_distance(
                base['latitude'], base['longitude'],
                pickup_lat, pickup_lon
            )
            if distance <= radius_miles and distance < min_distance:
                min_distance = distance
                assigned_base = base['name']
        
        return pd.Series({
            'pickup_distance_miles': min_distance if assigned_base else None,
            'assigned_base': assigned_base
        })
    
    # Apply distance calculation
    distance_info = df.apply(assign_base_and_distance, axis=1)
    df['pickup_distance_miles'] = distance_info['pickup_distance_miles']
    df['assigned_base'] = distance_info['assigned_base']
    
    # Filter tasks within radius (assigned to at least one base)
    df_within_radius = df[df['assigned_base'].notna()].copy()
    
    return df_within_radius


def calculate_compliance_rate(
    df: pd.DataFrame,
    expected_time: float
) -> Dict[str, Any]:
    """
    Calculate compliance rate (达标率) for tasks within radius.
    
    Returns:
        Dict with compliance statistics
    """
    if len(df) == 0:
        return {
            'total_tasks': 0,
            'compliant_tasks': 0,
            'compliance_rate': 0.0,
            'avg_response_time': 0.0
        }
    
    compliant_tasks = len(df[df['time_diff_minutes'] <= expected_time])
    total_tasks = len(df)
    compliance_rate = (compliant_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    avg_response_time = df['time_diff_minutes'].mean() if total_tasks > 0 else 0.0
    
    return {
        'total_tasks': int(total_tasks),
        'compliant_tasks': int(compliant_tasks),
        'compliance_rate': round(compliance_rate, 2),
        'avg_response_time': round(avg_response_time, 2)
    }


def calculate_range_statistics(
    base_names: List[str],
    radius_miles: float,
    expected_time: float
) -> Dict[str, Any]:
    """
    Calculate coverage statistics for bases.
    
    Returns:
        Dict with coverage stats, response time data, and compliance rate
    """
    # Load data
    df = read_data('FlightTransportsMaster.csv')
    df = df[df['PU State'] == 'Maine']
    
    # Get coordinates
    city_coords = get_city_coordinates(isOnlyMaine=True)
    base_locations = get_base_coordinates(base_names)
    
    # 1. Calculate coverage stats (cities covered by each base)
    coverage_stats = calculate_coverage_stats(base_locations, radius_miles, city_coords)
    
    # 2. Calculate response time and distance
    df_within_radius = calculate_response_time_and_distance(
        df, base_locations, radius_miles, city_coords
    )
    
    # 3. Calculate compliance rate
    compliance_stats = calculate_compliance_rate(df_within_radius, expected_time)
    
    # Prepare response time data (for frontend analysis)
    response_time_data = []
    if len(df_within_radius) > 0:
        response_time_data = df_within_radius[[
            'PU City', 'TASC Primary Asset ', 
            'time_diff_minutes', 'pickup_distance_miles'
        ]].to_dict(orient='records')
        
        # Replace NaN with None for JSON serialization
        for record in response_time_data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
    
    return {
        'coverage_stats': coverage_stats,  # e.g., {"BANGOR": 124, "PORTLAND": 98}
        'compliance_stats': compliance_stats,  # total_tasks, compliant_tasks, compliance_rate, avg_response_time
        'response_time_data': response_time_data  # List of tasks with time_diff_minutes and pickup_distance_miles
    }


def generate_range_map(
    base_names: List[str],
    radius_miles: float,
    expected_time: float,
    center_type: Optional[str] = None
) -> str:
    """
    Generate map with heatmap and service radius circles.
    
    Args:
        base_names: List of base city names
        radius_miles: Service radius in miles
        
    Returns:
        HTML string of the map
    """
    # Load data for heatmap
    df = read_data('FlightTransportsMaster.csv')
    df = df[df['PU State'] == 'Maine']
    if center_type:
        df = df[df['TASC Primary Asset '] == center_type]
    
    # Get city coordinates
    city_coords = get_city_coordinates(isOnlyMaine=True)
    
    # Process city demand for heatmap
    city_demand = process_city_demand(df, city_coords, isOnlyMaine=True)
    
    # Get base locations
    base_locations = get_base_coordinates(base_names)
    
    # Calculate center from base locations or city demand
    if len(base_locations) > 0:
        center_lat = sum(b['latitude'] for b in base_locations) / len(base_locations)
        center_lon = sum(b['longitude'] for b in base_locations) / len(base_locations)
    elif len(city_demand) > 0:
        center_lat = city_demand['latitude'].mean()
        center_lon = city_demand['longitude'].mean()
    else:
        center_lat = 44.5
        center_lon = -69.0
    

    if len(city_demand) > 0:
        m = create_heatmap(city_demand, center_lat=center_lat, center_lon=center_lon, zoom_start=7, radius=15)
    else:
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
    
    # Add base markers and circles
    for base in base_locations:
        # Add marker
        folium.Marker(
            location=[base['latitude'], base['longitude']],
            popup=f"<b>{base['name']}</b><br>Service Radius: {radius_miles} miles",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)
        
        # Add service radius circle
        folium.Circle(
            location=[base['latitude'], base['longitude']],
            radius=radius_miles * 1609.34,  # Convert miles to meters
            popup=f"{base['name']} - {radius_miles} mile radius",
            color='blue',
            fill=True,
            fillColor='blue',
            fillOpacity=0.1,
            weight=2
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Convert to HTML
    return map_to_html(m)

