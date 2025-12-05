import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any

from utils.heatmap import process_city_demand, get_city_coordinates


def load_dataset(dataset: str) -> pd.DataFrame:
    """
    Load dataset by name
    """
    data_dir = Path(__file__).parent.parent.parent / 'data' / '1_demand_forecasting'
    
    if dataset == 'Roux(2012-2023)':
        file_path = data_dir / 'data.csv'
        df = pd.read_csv(file_path, encoding='latin1')
    else:  # Master(2021-2024)
        file_path = data_dir / 'FlightTransportsMaster.csv'
        df = pd.read_csv(file_path, encoding='latin1')

    # only Maine
    df = df[df['PU State'] == 'Maine']
    return df


def filter_by_base(df: pd.DataFrame, base_places: str, dataset: str) -> pd.DataFrame:
    """
    Filter data by base places
    """
    if base_places == 'ALL':
        return df
    
    base_list = [b.strip() for b in base_places.split(',')]
    
    # Roux dataset uses 'veh' column, Master dataset uses 'TASC Primary Asset ' column
    if dataset == 'Roux(2012-2023)':
        if 'veh' in df.columns:
            df = df[df['veh'].isin(base_list)]
    else:
        if 'TASC Primary Asset ' in df.columns:
            df = df[df['TASC Primary Asset '].isin(base_list)]
    
    return df


def get_heatmap_by_base_data(dataset: str, base_places: str) -> Dict[str, Any]:
    """
    Get heatmap data for frontend rendering
    
    Args:
    dataset: dataset name
    base_places: base places list, comma separated or 'ALL'
    
    Returns:
    Dict with heatmap_data
    """
    # Load data
    df = load_dataset(dataset)
    
    # Filter data
    df = filter_by_base(df, base_places, dataset)
    
    # Get city coordinates
    city_coords = get_city_coordinates(isOnlyMaine=True)
    
    # Process city demand for heatmap
    city_demand = process_city_demand(df, city_coords, isOnlyMaine=True)
    
    # Convert city_demand to list of dicts for JSON serialization
    heatmap_data = []
    if len(city_demand) > 0:
        heatmap_data = city_demand[['latitude', 'longitude', 'task_count']].to_dict(orient='records')
        # Replace NaN with None for JSON serialization
        for record in heatmap_data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
    
    return {
        'heatmap_data': heatmap_data
    }