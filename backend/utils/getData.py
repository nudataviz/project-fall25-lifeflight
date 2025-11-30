import pandas as pd
import os

def read_data(fileName: str='data.csv') -> pd.DataFrame:
    """
    Read data from a CSV file.
    
    Args:
        fileName: Name of the CSV file
    Returns:
        DataFrame
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data','1_demand_forecasting', fileName)
    if fileName == 'data.csv':
        df = pd.read_csv(file_path, encoding='latin1')
    else:
        df = pd.read_csv(file_path)

    return df