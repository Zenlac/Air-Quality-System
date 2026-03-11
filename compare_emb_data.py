#!/usr/bin/env python3
"""
Compare original vs converted EMB data
"""

import pandas as pd
import sys
import os

def compare_emb_data():
    """Show the difference between original and converted EMB data"""
    
    print("=== EMB Data Comparison ===\n")
    
    # Check original EMB data
    original_file = 'EMB-CEPMOo1-year.csv'
    converted_file = 'EMB_converted.csv'
    
    print("1. Original EMB Data:")
    if os.path.exists(original_file):
        try:
            df_orig = pd.read_csv(original_file, nrows=5)
            print(f"   Columns: {list(df_orig.columns)}")
            print(f"   AQI values: {df_orig['AQI'].tolist()}")
            print(f"   Non-null AQI: {df_orig['AQI'].notna().sum()}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print(f"   File not found: {original_file}")
    
    print("\n2. Converted EMB Data:")
    if os.path.exists(converted_file):
        try:
            df_conv = pd.read_csv(converted_file, nrows=5)
            print(f"   Columns: {list(df_conv.columns)}")
            print(f"   AQI values: {df_conv['AQI'].tolist()}")
            print(f"   AQI range: {df_conv['AQI'].min():.2f} - {df_conv['AQI'].max():.2f}")
            print(f"   AQI std dev: {df_conv['AQI'].std():.2f}")
        except Exception as e:
            print(f"   Error: {e}")
    else:
        print(f"   File not found: {converted_file}")
        print("   Run 'python convert_emb_data.py' to create it")
    
    print("\n3. Recommendation:")
    print("   Use EMB_converted.csv in the web UI for best results!")

if __name__ == "__main__":
    compare_emb_data()
