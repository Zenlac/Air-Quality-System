#!/usr/bin/env python3
"""
Fix Zero AQI Values
This script fixes zero AQI values in the data
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

def fix_zero_aqi_values(input_file, output_file, method='mean'):
    """
    Fix zero AQI values in the data
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        method: Method to fix zeros ('mean', 'median', 'interpolate', 'remove')
    """
    
    print(f"Fixing zero AQI values in: {input_file}")
    print(f"Method: {method}")
    print(f"Output: {output_file}")
    
    # Load data
    df = pd.read_csv(input_file)
    print(f"Original data shape: {df.shape}")
    
    # Count zero AQI values
    zero_count = (df['AQI'] == 0).sum()
    print(f"Zero AQI values found: {zero_count}")
    
    if zero_count == 0:
        print("No zero AQI values found. Copying file as-is.")
        df.to_csv(output_file, index=False)
        return
    
    # Show rows with zero AQI
    zero_rows = df[df['AQI'] == 0].copy()
    print("\nRows with zero AQI:")
    print(zero_rows[['Timestamp', 'AQI']].head(10))
    
    # Fix zeros based on method
    df_fixed = df.copy()
    
    if method == 'mean':
        # Replace zeros with mean AQI
        mean_aqi = df[df['AQI'] > 0]['AQI'].mean()
        print(f"\nReplacing zeros with mean AQI: {mean_aqi:.2f}")
        df_fixed.loc[df_fixed['AQI'] == 0, 'AQI'] = mean_aqi
        
    elif method == 'median':
        # Replace zeros with median AQI
        median_aqi = df[df['AQI'] > 0]['AQI'].median()
        print(f"\nReplacing zeros with median AQI: {median_aqi:.2f}")
        df_fixed.loc[df_fixed['AQI'] == 0, 'AQI'] = median_aqi
        
    elif method == 'interpolate':
        # Interpolate zeros
        print("\nInterpolating zero AQI values...")
        df_fixed['AQI'] = df_fixed['AQI'].replace(0, np.nan)
        df_fixed['AQI'] = df_fixed['AQI'].interpolate(method='linear')
        
    elif method == 'remove':
        # Remove rows with zero AQI
        print(f"\nRemoving {zero_count} rows with zero AQI")
        df_fixed = df_fixed[df_fixed['AQI'] > 0].copy()
        
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Verify fix
    new_zero_count = (df_fixed['AQI'] == 0).sum()
    print(f"\nZero AQI values after fix: {new_zero_count}")
    print(f"Fixed data shape: {df_fixed.shape}")
    
    # Show AQI statistics
    print(f"\nAQI Statistics:")
    print(f"  Min: {df_fixed['AQI'].min():.2f}")
    print(f"  Max: {df_fixed['AQI'].max():.2f}")
    print(f"  Mean: {df_fixed['AQI'].mean():.2f}")
    print(f"  Median: {df_fixed['AQI'].median():.2f}")
    
    # Save fixed data
    df_fixed.to_csv(output_file, index=False)
    print(f"\nFixed data saved to: {output_file}")
    
    return df_fixed

def create_clean_sample_data():
    """Create a clean version of sample data without zeros"""
    
    input_file = 'csv_files/data_files/sample_air_quality_data.csv'
    output_file = 'csv_files/data_files/sample_air_quality_data_clean.csv'
    
    print("Creating clean sample data...")
    
    # Use median method (most robust for outliers)
    fix_zero_aqi_values(input_file, output_file, method='median')
    
    print(f"\nClean sample data created: {output_file}")
    print("You can use this file for testing without zero AQI issues.")

def compare_datasets():
    """Compare original and fixed datasets"""
    
    original_file = 'csv_files/data_files/sample_air_quality_data.csv'
    fixed_file = 'csv_files/data_files/sample_air_quality_data_clean.csv'
    
    if not os.path.exists(fixed_file):
        print("Fixed file not found. Run create_clean_sample_data() first.")
        return
    
    print("\nComparing datasets:")
    print("-" * 30)
    
    # Load both datasets
    df_orig = pd.read_csv(original_file)
    df_fixed = pd.read_csv(fixed_file)
    
    print(f"Original dataset: {df_orig.shape}")
    print(f"Fixed dataset: {df_fixed.shape}")
    
    print(f"\nOriginal AQI stats:")
    print(f"  Zeros: {(df_orig['AQI'] == 0).sum()}")
    print(f"  Mean: {df_orig['AQI'].mean():.2f}")
    print(f"  Min: {df_orig['AQI'].min():.2f}")
    print(f"  Max: {df_orig['AQI'].max():.2f}")
    
    print(f"\nFixed AQI stats:")
    print(f"  Zeros: {(df_fixed['AQI'] == 0).sum()}")
    print(f"  Mean: {df_fixed['AQI'].mean():.2f}")
    print(f"  Min: {df_fixed['AQI'].min():.2f}")
    print(f"  Max: {df_fixed['AQI'].max():.2f}")

if __name__ == "__main__":
    print("Zero AQI Fix Utility")
    print("=" * 40)
    
    # Create clean sample data
    create_clean_sample_data()
    
    # Compare datasets
    compare_datasets()
    
    print("\n" + "=" * 40)
    print("Summary:")
    print("1. Created clean sample data without zero AQI values")
    print("2. Used median replacement method (robust to outliers)")
    print("3. Original file preserved for reference")
    print("4. Clean file ready for use in the system")
    
    print("\nUsage:")
    print("- Use 'sample_air_quality_data_clean.csv' for testing")
    print("- Original file remains unchanged")
    print("- System should work better with clean data")
