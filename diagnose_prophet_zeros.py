#!/usr/bin/env python3
"""
Diagnose Prophet Model Zero Values Issue
This script helps identify why Prophet model might be producing zero values
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def diagnose_prophet_issue():
    """Diagnose Prophet model zero values issue"""
    
    print("Diagnosing Prophet Model Zero Values Issue")
    print("=" * 60)
    
    try:
        # Import required modules
        from prophet_trainer import ProphetTrainer
        from config import Config
        
        print("Imports successful")
        
        # Load sample data
        data_path = 'csv_files/data_files/sample_air_quality_data.csv'
        print(f"Loading data from: {data_path}")
        
        df = pd.read_csv(data_path)
        print(f"Data loaded successfully: {df.shape}")
        
        # Check data structure
        print("\nData Structure Analysis:")
        print(f"Columns: {list(df.columns)}")
        print(f"Data types: {df.dtypes.to_dict()}")
        print(f"AQI range: {df['AQI'].min():.2f} to {df['AQI'].max():.2f}")
        print(f"AQI mean: {df['AQI'].mean():.2f}")
        print(f"Zero AQI values: {(df['AQI'] == 0).sum()}")
        print(f"Missing AQI values: {df['AQI'].isna().sum()}")
        
        # Check for negative values
        negative_aqi = (df['AQI'] < 0).sum()
        print(f"Negative AQI values: {negative_aqi}")
        
        # Check date range
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        print(f"Date range: {df['Timestamp'].min().date()} to {df['Timestamp'].max().date()}")
        print(f"Number of days: {(df['Timestamp'].max() - df['Timestamp'].min()).days}")
        
        # Initialize Prophet trainer
        config = Config('config.yaml')
        prophet_trainer = ProphetTrainer(config)
        print("\nProphet trainer initialized")
        
        # Prepare data for Prophet
        print("\nPreparing data for Prophet...")
        prophet_df = prophet_trainer._prepare_prophet_data(df)
        print(f"Data prepared: {prophet_df.shape}")
        
        # Check prepared data
        print("\nPrepared Data Analysis:")
        print(f"Columns: {list(prophet_df.columns)}")
        print(f"Data types: {prophet_df.dtypes.to_dict()}")
        print(f"y (AQI) range: {prophet_df['y'].min():.2f} to {prophet_df['y'].max():.2f}")
        print(f"y (AQI) mean: {prophet_df['y'].mean():.2f}")
        print(f"Zero y values: {(prophet_df['y'] == 0).sum()}")
        print(f"Missing y values: {prophet_df['y'].isna().sum()}")
        
        # Check for any data issues
        print("\nData Quality Checks:")
        
        # Check for constant values
        if prophet_df['y'].nunique() == 1:
            print("WARNING: AQI has only one unique value - Prophet will predict this constant")
        else:
            print(f"AQI has {prophet_df['y'].nunique()} unique values")
        
        # Check for very low variance
        variance = prophet_df['y'].var()
        if variance < 1.0:
            print(f"WARNING: Very low variance ({variance:.4f}) - Prophet may struggle")
        else:
            print(f"Good variance: {variance:.4f}")
        
        # Check date continuity
        date_diffs = prophet_df['ds'].diff().dt.days.dropna()
        if date_diffs.max() > 1:
            print(f"WARNING: Gaps in data - max gap: {date_diffs.max()} days")
        else:
            print("Continuous daily data")
        
        # Try to train Prophet model
        print("\nTraining Prophet model...")
        try:
            model = prophet_trainer.train(df)
            print("Prophet model trained successfully")
            
            # Make a prediction to test
            print("\nTesting predictions...")
            future = model.make_future_dataframe(periods=7)
            forecast = model.predict(future)
            
            # Check predictions
            print(f"Predictions generated: {forecast.shape}")
            print(f"Prediction range: {forecast['yhat'].min():.2f} to {forecast['yhat'].max():.2f}")
            print(f"Zero predictions: {(forecast['yhat'] == 0).sum()}")
            print(f"Negative predictions: {(forecast['yhat'] < 0).sum()}")
            
            # Show first few predictions
            print("\nSample Predictions:")
            print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(10))
            
            # Check if predictions are suspiciously close to zero
            mean_prediction = forecast['yhat'].mean()
            if mean_prediction < 1.0:
                print(f"\nWARNING: Mean prediction is very low ({mean_prediction:.4f})")
                print("   This could indicate:")
                print("   - Data preprocessing issues")
                print("   - Prophet configuration problems")
                print("   - Data scaling issues")
            else:
                print(f"\nMean prediction looks reasonable: {mean_prediction:.2f}")
            
        except Exception as e:
            print(f"Prophet training failed: {e}")
            return False
        
        print("\nDiagnosis Complete!")
        return True
        
    except Exception as e:
        print(f"Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_common_issues():
    """Check for common issues that cause Prophet to produce zeros"""
    
    print("\nCommon Issues Check:")
    print("-" * 30)
    
    issues = []
    
    # Check data file
    data_path = 'csv_files/data_files/sample_air_quality_data.csv'
    if not os.path.exists(data_path):
        issues.append("Sample data file not found")
    else:
        df = pd.read_csv(data_path)
        
        # Check for zero AQI values
        zero_count = (df['AQI'] == 0).sum()
        if zero_count > 0:
            issues.append(f"Found {zero_count} zero AQI values in data")
        
        # Check for negative AQI values
        neg_count = (df['AQI'] < 0).sum()
        if neg_count > 0:
            issues.append(f"Found {neg_count} negative AQI values")
        
        # Check for very small values
        small_count = (df['AQI'] < 1.0).sum()
        if small_count > len(df) * 0.5:  # More than 50% small values
            issues.append(f"Found {small_count} AQI values < 1.0 (more than 50%)")
        
        # Check data range
        aqi_range = df['AQI'].max() - df['AQI'].min()
        if aqi_range < 10:
            issues.append(f"Very small AQI range: {aqi_range:.2f}")
    
    if issues:
        print("Potential Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("No common issues detected")
    
    return len(issues) == 0

if __name__ == "__main__":
    print("Starting Prophet Diagnosis")
    print("=" * 60)
    
    # Check common issues first
    common_ok = check_common_issues()
    
    # Run full diagnosis
    diagnosis_ok = diagnose_prophet_issue()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"Common Issues Check: {'PASS' if common_ok else 'ISSUES FOUND'}")
    print(f"Full Diagnosis: {'PASS' if diagnosis_ok else 'FAILED'}")
    
    if not common_ok or not diagnosis_ok:
        print("\nRecommendations:")
        print("1. Check data quality - ensure AQI values are reasonable")
        print("2. Verify data preprocessing isn't introducing zeros")
        print("3. Review Prophet configuration parameters")
        print("4. Consider data scaling if values are very small")
        print("5. Check for data leakage or preprocessing errors")
    else:
        print("\nProphet model appears to be working correctly!")
