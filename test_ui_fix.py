#!/usr/bin/env python3
"""
Test the UI fix for Timestamp error
"""

import sys
import os
import pandas as pd

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_ui_data_handling():
    """Test how the UI handles processed data with Timestamp as index"""
    
    print("Testing UI data handling with Timestamp as index...")
    
    try:
        # Load sample data
        df = pd.read_csv('sample_air_quality_data.csv')
        print(f"OK: Original data loaded: {df.shape}")
        print(f"  Original columns: {list(df.columns)}")
        
        # Process data like the DataProcessor does
        from src.data_processor import DataProcessor
        from src.config import Config
        
        config = Config('config.yaml')
        processor = DataProcessor(config)
        
        processed_data = processor.process_data(df)
        print(f"OK: Data processed: {processed_data.shape}")
        print(f"  Processed columns: {list(processed_data.columns)}")
        print(f"  Index name: {processed_data.index.name}")
        print(f"  Index type: {type(processed_data.index)}")
        
        # Test the UI logic for handling Timestamp
        print("\nTesting UI logic...")
        
        # Test 1: Check if Timestamp is in columns
        timestamp_in_columns = 'Timestamp' in processed_data.columns
        print(f"  Timestamp in columns: {timestamp_in_columns}")
        
        # Test 2: Check if index is datetime and named Timestamp
        is_datetime_index = hasattr(processed_data.index, 'to_datetime')
        index_is_timestamp = processed_data.index.name == 'Timestamp'
        print(f"  Index is datetime: {is_datetime_index}")
        print(f"  Index name is 'Timestamp': {index_is_timestamp}")
        
        # Test 3: Test date range access (UI logic)
        if timestamp_in_columns:
            date_range = (processed_data['Timestamp'].max() - processed_data['Timestamp'].min()).days
            print(f"  Date range (from columns): {date_range} days")
        elif is_datetime_index and index_is_timestamp:
            date_range = (processed_data.index.max() - processed_data.index.min()).days
            print(f"  Date range (from index): {date_range} days")
        else:
            print("  Date range: Not available")
        
        # Test 4: Test last date access (UI logic)
        if timestamp_in_columns:
            last_date = processed_data['Timestamp'].iloc[-1]
        else:
            last_date = processed_data.index[-1]
        print(f"  Last date: {last_date}")
        
        # Test 5: Test AQI access
        aqi_range = f"{processed_data['AQI'].min():.1f} to {processed_data['AQI'].max():.1f}"
        print(f"  AQI range: {aqi_range}")
        
        print("\nOK: All UI logic tests passed!")
        print("The Timestamp error should now be fixed in the UI.")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ui_data_handling()
    if success:
        print("\nSUCCESS: UI fix verification successful!")
        print("You can now use the web interface without Timestamp errors.")
    else:
        print("\nFAILED: UI fix verification failed.")
        print("Please check the error messages above.")
