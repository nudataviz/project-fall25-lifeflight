import pandas as pd
import os
from pathlib import Path

from utils.heatmap import generate_city_demand_heatmap, map_to_html


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


def generate_heatmap_by_base(dataset: str, base_places: str) -> str:
    """
    Generate heatmap HTML
    
    Args:
    dataset: dataset name
    base_places: base places list, comma separated or 'ALL'
    
    Returns:
    HTML string
    """
    # Load data
    df = load_dataset(dataset)
    
    # Filter data
    df = filter_by_base(df, base_places, dataset)
    
    # Generate heatmap
    map_obj = generate_city_demand_heatmap(df, zoom_start=7, radius=15, isOnlyMaine=True)
    
    # Convert to HTML
    html_map = map_to_html(map_obj)
    
    return html_map