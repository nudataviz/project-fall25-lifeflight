import pandas as pd

def get_time_diff_seconds(df: pd.DataFrame, start_time_col: str, end_time_col: str) -> pd.Series:
    """
    Calculate the time difference between two time columns (in seconds)
    
    Args:
    df: DataFrame
    start_time_col: str, the column name of the first time
    end_time_col: str, the column name of the second time
    
    Returns:
    Series, the time difference in seconds (float)
    """
    # Convert time columns to datetime type
    start_time = pd.to_datetime(df[start_time_col], errors='coerce')
    end_time = pd.to_datetime(df[end_time_col], errors='coerce')
    
    # Calculate time difference (in seconds)
    time_diff = (end_time - start_time).dt.total_seconds()
    
    return time_diff