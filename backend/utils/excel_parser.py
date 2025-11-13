"""
Excel file parsing utilities for population data.

This module provides functions to parse Excel files containing population data:
- Parse population projection files (2024-2042)
- Parse historical city/town population files (2010-2020)
"""

import pandas as pd
import os
from typing import Optional, Dict, List


def parse_county_population_projections(
    file_path: str,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Parse MaineStateCountyPopulationProjections2042.xlsx
    
    Args:
        file_path: Path to Excel file
        output_path: Optional path to save parsed data
        
    Returns:
        DataFrame with county population projections
    """
    try:
        # Read Excel file
        # Note: Excel files may have multiple sheets, try to read all
        excel_file = pd.ExcelFile(file_path)
        
        # Print available sheets for debugging
        print(f"Available sheets: {excel_file.sheet_names}")
        
        # Try to read the first sheet (or all sheets)
        # Common sheet names: 'Sheet1', 'Data', 'Projections', etc.
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Clean and process data
        # Note: Structure may vary, need to inspect first
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head()}")
        
        # Return raw data for now (structure may vary)
        if output_path:
            df.to_csv(output_path, index=False)
            print(f"County population projections saved to {output_path}")
        
        return df
        
    except Exception as e:
        print(f"Error parsing county population projections: {e}")
        return pd.DataFrame()


def parse_city_population_projections(
    file_path: str,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Parse MaineCityTownPopulationProjection2042.xlsx
    
    Args:
        file_path: Path to Excel file
        output_path: Optional path to save parsed data
        
    Returns:
        DataFrame with city/town population projections
    """
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        
        # Print available sheets for debugging
        print(f"Available sheets: {excel_file.sheet_names}")
        
        # Try to read the first sheet
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Clean and process data
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head()}")
        
        # Return raw data for now (structure may vary)
        if output_path:
            df.to_csv(output_path, index=False)
            print(f"City/town population projections saved to {output_path}")
        
        return df
        
    except Exception as e:
        print(f"Error parsing city population projections: {e}")
        return pd.DataFrame()


def parse_historical_city_population(
    file_path: str,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Parse Total Population for Maine Cities and Towns (2010-2019).xlsx
    
    Args:
        file_path: Path to Excel file
        output_path: Optional path to save parsed data
        
    Returns:
        DataFrame with historical city/town population
    """
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        
        # Print available sheets for debugging
        print(f"Available sheets: {excel_file.sheet_names}")
        
        # Try to read the first sheet
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Clean and process data
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head()}")
        
        # Return raw data for now (structure may vary)
        if output_path:
            df.to_csv(output_path, index=False)
            print(f"Historical city/town population saved to {output_path}")
        
        return df
        
    except Exception as e:
        print(f"Error parsing historical city population: {e}")
        return pd.DataFrame()


def parse_2020_city_population(
    file_path: str,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Parse Total Population_2020_3.xlsx
    
    Args:
        file_path: Path to Excel file
        output_path: Optional path to save parsed data
        
    Returns:
        DataFrame with 2020 city/town population
    """
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        
        # Print available sheets for debugging
        print(f"Available sheets: {excel_file.sheet_names}")
        
        # Try to read the first sheet
        df = pd.read_excel(file_path, sheet_name=0)
        
        # Clean and process data
        print(f"Columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head()}")
        
        # Return raw data for now (structure may vary)
        if output_path:
            df.to_csv(output_path, index=False)
            print(f"2020 city/town population saved to {output_path}")
        
        return df
        
    except Exception as e:
        print(f"Error parsing 2020 city population: {e}")
        return pd.DataFrame()


def parse_all_excel_files(
    data_dir: str = 'data/1_demand_forecasting',
    output_dir: Optional[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Parse all Excel population files.
    
    Args:
        data_dir: Directory containing Excel files
        output_dir: Optional output directory for parsed data
        
    Returns:
        Dictionary of parsed DataFrames
    """
    if output_dir is None:
        output_dir = os.path.join(data_dir, '..', 'processed')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    
    # 1. Parse county population projections
    print("Parsing county population projections...")
    county_projections = parse_county_population_projections(
        os.path.join(data_dir, 'MaineStateCountyPopulationProjections2042.xlsx'),
        os.path.join(output_dir, 'county_population_projections.csv')
    )
    results['county_projections'] = county_projections
    
    # 2. Parse city/town population projections
    print("\nParsing city/town population projections...")
    city_projections = parse_city_population_projections(
        os.path.join(data_dir, 'MaineCityTownPopulationProjection2042.xlsx'),
        os.path.join(output_dir, 'city_population_projections.csv')
    )
    results['city_projections'] = city_projections
    
    # 3. Parse historical city/town population
    print("\nParsing historical city/town population...")
    historical_city_pop = parse_historical_city_population(
        os.path.join(data_dir, 'Total Population for Maine Cities and Towns (2010-2019).xlsx'),
        os.path.join(output_dir, 'historical_city_population.csv')
    )
    results['historical_city_pop'] = historical_city_pop
    
    # 4. Parse 2020 city/town population
    print("\nParsing 2020 city/town population...")
    city_pop_2020 = parse_2020_city_population(
        os.path.join(data_dir, 'Total Population_2020_3.xlsx'),
        os.path.join(output_dir, 'city_population_2020.csv')
    )
    results['city_pop_2020'] = city_pop_2020
    
    print("\nAll Excel files parsed!")
    return results


if __name__ == '__main__':
    # Example usage
    import sys
    
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data/1_demand_forecasting'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'data/processed'
    
    results = parse_all_excel_files(data_dir, output_dir)
    
    print("\n=== Parsing Summary ===")
    for key, df in results.items():
        print(f"{key}: {len(df)} rows")

