import json
import os
import pandas as pd
from typing import Dict, Tuple, Optional


def get_city_coordinates(isOnlyMaine: bool = False) -> Dict[str, Tuple[float, float]]:
    """
    Load city coordinates from JSON file.
    """
    # city_coordinates is nationwide coordinates
    # maine_city_coordinates is the coordinates only for maine cities
    if isOnlyMaine:
        with open(os.path.join(os.path.dirname(__file__), '..','data', 'maine_city_coordinates.json'), 'r') as f:
            city_coordinates = json.load(f)
    else:
        with open(os.path.join(os.path.dirname(__file__), '..','data', 'city_coordinates.json'), 'r') as f:
            city_coordinates = json.load(f)
    return city_coordinates


def process_city_demand(
    df: pd.DataFrame,
    city_coordinates: Optional[Dict[str, Tuple[float, float]]] = None,
    isOnlyMaine: bool = False
) -> pd.DataFrame:
    """
    Process city demand data and add coordinate information.
    """
    if city_coordinates is None:
        city_coordinates = get_city_coordinates(isOnlyMaine)
    
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