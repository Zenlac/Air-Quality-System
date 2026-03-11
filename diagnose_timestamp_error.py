#!/usr/bin/env python3
"""
Diagnose timestamp error with sample data
"""

import pandas as pd
import sys
import os

def diagnose_sample_data():
    """Diagnose potential issues with sample data"""
    
    print("=== TIMESTAMP ERROR DIAGNOSIS ===\n")
    
    file_path = 'sample_air_quality_data.csv'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} not found!")
        return
    
    print(f"OK: File found: {file_path}")
    
    try:
        # Test 1: Basic CSV loading
        print("\n1. Testing basic CSV loading...")
        df = pd.read_csv(file_path)
        print(f"   OK: CSV loaded successfully")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        # Test 2: Check required columns
        print("\n2. Checking required columns...")
        required_columns = ['Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 'NH3', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"   ERROR: Missing columns: {missing_columns}")
        else:
            print(f"   OK: All required columns present")
        
        # Test 3: Check Timestamp column specifically
        print("\n3. Testing Timestamp column...")
        if 'Timestamp' in df.columns:
            print(f"   OK: Timestamp column found")
            print(f"   Sample values: {df['Timestamp'].head(3).tolist()}")
            
            # Test timestamp parsing
            try:
                df_parsed = pd.read_csv(file_path, parse_dates=['Timestamp'])
                print(f"   OK: Timestamp parsing successful")
                print(f"   Data types: {df_parsed.dtypes['Timestamp']}")
            except Exception as e:
                print(f"   ERROR: Timestamp parsing failed: {e}")
        else:
            print(f"   ERROR: Timestamp column missing")
        
        # Test 4: Check AQI column
        print("\n4. Testing AQI column...")
        if 'AQI' in df.columns:
            print(f"   OK: AQI column found")
            print(f"   Non-null values: {df['AQI'].notna().sum()}")
            print(f"   Sample values: {df['AQI'].head(3).tolist()}")
            
            if df['AQI'].isna().all():
                print(f"   ERROR: AQI column is completely empty")
            else:
                print(f"   OK: AQI column has values")
        else:
            print(f"   ERROR: AQI column missing")
        
        # Test 5: Try full data processor loading
        print("\n5. Testing data processor loading...")
        try:
            sys.path.append('src')
            from src.data_processor import DataProcessor
            from src.config import Config
            
            config = Config('config.yaml')
            processor = DataProcessor(config)
            
            df_processed = processor.load_data(file_path)
            print(f"   OK: Data processor loading successful")
            print(f"   Processed shape: {df_processed.shape}")
            
        except Exception as e:
            print(f"   ERROR: Data processor loading failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 6: Try full system
        print("\n6. Testing full system...")
        try:
            from src.config import Config
            from src.data_processor import DataProcessor
            from src.model_trainer import ModelTrainer
            
            config = Config('config.yaml')
            processor = DataProcessor(config)
            trainer = ModelTrainer(config)
            
            df = processor.load_data(file_path)
            processed_data = processor.process_data(df)
            
            prophet_model = trainer.train_prophet(processed_data)
            print(f"   OK: Prophet model training successful")
            
            arima_model = trainer.train_arima(processed_data)
            print(f"   OK: ARIMA model training successful")
            
        except Exception as e:
            print(f"   ERROR: Full system test failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_sample_data()
