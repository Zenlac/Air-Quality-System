#!/usr/bin/env python3
"""
Diagnose Data Processing Error
This script helps identify and fix data processing errors in the system
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def diagnose_data_processing():
    """Diagnose data processing issues"""
    
    print("Diagnosing Data Processing Error")
    print("=" * 60)
    
    try:
        # Import required modules
        from data_processor import DataProcessor
        from config import Config
        
        print("Imports successful")
        
        # Test with sample data
        data_path = 'csv_files/data_files/sample_air_quality_data.csv'
        print(f"Testing with: {data_path}")
        
        # Step 1: Load raw data
        print("\nStep 1: Loading raw data...")
        df = pd.read_csv(data_path)
        print(f"Raw data loaded: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for basic issues
        print("\nBasic Data Check:")
        print(f"Data types: {df.dtypes.to_dict()}")
        print(f"Missing values: {df.isnull().sum().to_dict()}")
        print(f"AQI range: {df['AQI'].min():.2f} to {df['AQI'].max():.2f}")
        print(f"Zero AQI values: {(df['AQI'] == 0).sum()}")
        
        # Step 2: Initialize data processor
        print("\nStep 2: Initializing DataProcessor...")
        config = Config('config.yaml')
        processor = DataProcessor(config)
        print("DataProcessor initialized")
        
        # Step 3: Test data loading
        print("\nStep 3: Testing data loading...")
        try:
            loaded_data = processor.load_data(data_path)
            print(f"Data loaded successfully: {loaded_data.shape}")
            print(f"Columns after loading: {list(loaded_data.columns)}")
        except Exception as e:
            print(f"Data loading failed: {e}")
            return False
        
        # Step 4: Test data processing
        print("\nStep 4: Testing data processing...")
        try:
            processed_data = processor.process_data(loaded_data)
            print(f"Data processed successfully: {processed_data.shape}")
            print(f"Columns after processing: {list(processed_data.columns)}")
            
            # Check processed data quality
            print("\nProcessed Data Quality:")
            print(f"Data types: {processed_data.dtypes.to_dict()}")
            print(f"Missing values: {processed_data.isnull().sum().to_dict()}")
            
            if 'AQI' in processed_data.columns:
                print(f"AQI range: {processed_data['AQI'].min():.2f} to {processed_data['AQI'].max():.2f}")
                print(f"Zero AQI values: {(processed_data['AQI'] == 0).sum()}")
            
            # Check index
            print(f"Index type: {type(processed_data.index)}")
            print(f"Index name: {processed_data.index.name}")
            
        except Exception as e:
            print(f"Data processing failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\nData processing successful!")
        return True
        
    except Exception as e:
        print(f"Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_common_data_issues():
    """Check for common data issues"""
    
    print("\nCommon Data Issues Check:")
    print("-" * 30)
    
    data_path = 'csv_files/data_files/sample_air_quality_data.csv'
    
    if not os.path.exists(data_path):
        print("Sample data file not found")
        return False
    
    df = pd.read_csv(data_path)
    issues = []
    
    # Check required columns
    required_columns = ['Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 'NH3', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
    
    # Check data types
    if 'Timestamp' in df.columns:
        try:
            pd.to_datetime(df['Timestamp'])
        except:
            issues.append("Timestamp column cannot be converted to datetime")
    
    # Check AQI values
    if 'AQI' in df.columns:
        if df['AQI'].isnull().any():
            issues.append(f"Missing AQI values: {df['AQI'].isnull().sum()}")
        
        if (df['AQI'] < 0).any():
            issues.append(f"Negative AQI values: {(df['AQI'] < 0).sum()}")
        
        zero_count = (df['AQI'] == 0).sum()
        if zero_count > 0:
            issues.append(f"Zero AQI values: {zero_count}")
    
    # Check data size
    if len(df) < 10:
        issues.append(f"Very small dataset: {len(df)} rows")
    
    if issues:
        print("Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("No common issues detected")
    
    return len(issues) == 0

def suggest_fixes():
    """Suggest fixes for common issues"""
    
    print("\nSuggested Fixes:")
    print("-" * 20)
    
    print("1. For missing columns:")
    print("   - Ensure CSV has exactly 14 required columns")
    print("   - Check column names match exactly (case-sensitive)")
    
    print("\n2. For timestamp issues:")
    print("   - Ensure Timestamp column is in YYYY-MM-DD format")
    print("   - Remove any extra spaces or special characters")
    
    print("\n3. For AQI issues:")
    print("   - Replace missing AQI values with mean/median")
    print("   - Remove or replace zero/negative AQI values")
    print("   - Ensure AQI values are numeric")
    
    print("\n4. For small datasets:")
    print("   - Collect more data if possible")
    print("   - Use simplified models for small datasets")
    
    print("\n5. General fixes:")
    print("   - Check for extra spaces in column names")
    print("   - Ensure CSV format is correct")
    print("   - Remove any special characters in data")

if __name__ == "__main__":
    print("Starting Data Processing Diagnosis")
    print("=" * 60)
    
    # Check common issues
    common_ok = check_common_data_issues()
    
    # Run full diagnosis
    processing_ok = diagnose_data_processing()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"Common Issues Check: {'PASS' if common_ok else 'ISSUES FOUND'}")
    print(f"Data Processing: {'PASS' if processing_ok else 'FAILED'}")
    
    if not common_ok or not processing_ok:
        suggest_fixes()
    else:
        print("\nData processing appears to be working correctly!")
