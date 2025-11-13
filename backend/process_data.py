#!/usr/bin/env python3
"""
Script to process all data files.

Usage:
    python process_data.py [data_dir] [output_dir]
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_processing import process_all_data

if __name__ == '__main__':
    # Get data directory from command line or use default
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'data/processed'
    
    print(f"Processing data from: {data_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Process all data
    results = process_all_data(data_dir, output_dir)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Processing Summary")
    print("=" * 50)
    for key, df in results.items():
        print(f"{key}: {len(df)} rows")
        if len(df) > 0:
            print(f"  Columns: {list(df.columns)}")
            print(f"  Sample:")
            print(df.head(3))
            print()

