import folium
import json
import os
from folium.plugins import HeatMap
import pandas as pd
from typing import Dict, Tuple, Optional


def get_city_coordinates() -> Dict[str, Tuple[float, float]]:
    """
    Load city coordinates from JSON file.
    """
    # city_coordinates is nationwide coordinates
    # maine_city_coordinates is the coordinates only for maine cities
    with open(os.path.join(os.path.dirname(__file__), '..','data', 'city_coordinates.json'), 'r') as f:
        city_coordinates = json.load(f)
    return city_coordinates


def process_city_demand(
    df: pd.DataFrame,
    city_coordinates: Optional[Dict[str, Tuple[float, float]]] = None
) -> pd.DataFrame:
    """
    Process city demand data and add coordinate information.
    """
    if city_coordinates is None:
        city_coordinates = get_city_coordinates()
    
    # Aggregate task demand by city
    city_demand = df.groupby('PU City').size().reset_index(name='task_count')
    
    # Add coordinates
    city_demand['latitude'] = city_demand['PU City'].apply(
        lambda x: city_coordinates.get(x, (None, None))[0]
    )
    city_demand['longitude'] = city_demand['PU City'].apply(
        lambda x: city_coordinates.get(x, (None, None))[1]
    )

    city_demand.dropna(subset=['latitude', 'longitude'], inplace=True)
    
    return city_demand


def create_heatmap(
    city_demand: pd.DataFrame,
    center_lat: Optional[float] = None,
    center_lon: Optional[float] = None,
    zoom_start: int = 6,
    radius: int = 10
) -> folium.Map:
    """
    Create a heatmap visualization
    """
    if center_lat is None:
        center_lat = city_demand['latitude'].mean()
    if center_lon is None:
        center_lon = city_demand['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start
    )
    heatmap_data = city_demand[['latitude', 'longitude', 'task_count']].values.tolist()
    
    # Add heatmap layer
    HeatMap(data=heatmap_data, radius=radius).add_to(m)
    
    return m

def generate_city_demand_heatmap(
    df: pd.DataFrame,
    city_coordinates: Optional[Dict[str, Tuple[float, float]]] = None,
    zoom_start: int = 6,
    radius: int = 10
) -> folium.Map:
    """
    Complete workflow: Generate heatmap from raw data
    """
    # Process data
    city_demand = process_city_demand(df, city_coordinates)
    
    # Generate map
    m = create_heatmap(city_demand, zoom_start=zoom_start, radius=radius)
    
    return m

def map_to_html(map_obj: folium.Map) -> str:
    """
    Convert folium map object to HTML string.
    """
    return map_obj._repr_html_()