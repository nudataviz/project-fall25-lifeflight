"""
Utility functions to prepare boxplot data for vehicle mileage distribution.
"""

from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import numpy as np


VEH_ORDER = ['LF1', 'LF2', 'LF3', 'LF4']
MILEAGE_COLUMN = 'Mileage - Loaded'
VEH_COLUMN = 'veh'


def _load_clean_data() -> pd.DataFrame:
    """
    Load and clean the vehicle mileage dataset.

    Returns:
        Cleaned pandas DataFrame with numeric mileage and valid vehicle codes.
    """
    data_path = (
        Path(__file__)
        .resolve()
        .parents[2]
        / 'data'
        / '2_scenario_modeling'
        / 'roux_clean_veh_data.csv'
    )

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(data_path)

    if VEH_COLUMN not in df.columns or MILEAGE_COLUMN not in df.columns:
        raise ValueError(
            f"Required columns '{VEH_COLUMN}' and '{MILEAGE_COLUMN}' "
            f"not found in dataset: {data_path}"
        )

    df[MILEAGE_COLUMN] = (
        pd.to_numeric(df[MILEAGE_COLUMN], errors='coerce')
        .fillna(np.nan)
    )

    df = df.dropna(subset=[MILEAGE_COLUMN])
    df = df[df[MILEAGE_COLUMN] >= 0]

    df[VEH_COLUMN] = df[VEH_COLUMN].astype(str).str.strip()
    df = df[df[VEH_COLUMN].isin(VEH_ORDER)]

    return df


def _compute_summary(values: pd.Series) -> Dict[str, float]:
    """
    Compute summary statistics needed for boxplot and tooltip.
    """
    summary = values.describe(percentiles=[0.25, 0.5, 0.75])
    return {
        'count': int(summary['count']),
        'mean': float(summary['mean']),
        'std': float(summary['std']) if not pd.isna(summary['std']) else 0.0,
        'min': float(summary['min']),
        'q1': float(summary['25%']),
        'median': float(summary['50%']),
        'q3': float(summary['75%']),
        'max': float(summary['max']),
    }


def get_boxplot() -> Dict[str, Any]:
    """
    Prepare boxplot data - returns raw data rows plus summary statistics.

    Returns:
        Dict containing:
        - data: List of raw data rows with 'veh' and 'mileage' fields
        - summary: Dict of summary statistics per vehicle
        - metadata: Dataset metadata
    """
    df = _load_clean_data()

    # Prepare raw data rows for frontend (Observable Plot boxY format)
    raw_data = []
    for _, row in df.iterrows():
        raw_data.append({
            'veh': str(row[VEH_COLUMN]).strip(),
            'mileage': round(float(row[MILEAGE_COLUMN]), 2)
        })

    # Compute summary statistics per vehicle
    summary_by_veh: Dict[str, Dict[str, float]] = {}
    for veh in VEH_ORDER:
        subset = df[df[VEH_COLUMN] == veh][MILEAGE_COLUMN]
        if not subset.empty:
            summary_by_veh[veh] = _compute_summary(subset)

    return {
        'data': raw_data,
        'summary': summary_by_veh
    }
