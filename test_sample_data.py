#!/usr/bin/env python3
"""
Simple test to reproduce the timestamp error
"""

import sys
import os

def test_sample_data():
    """Test sample data with minimal setup"""
    
    print("Testing sample data with minimal setup...")
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Test 1: Import modules
        print("1. Importing modules...")
        from src.config import Config
        from src.data_processor import DataProcessor
        print("   OK: Modules imported")
        
        # Test 2: Load config
        print("2. Loading config...")
        config = Config('config.yaml')
        print("   OK: Config loaded")
        
        # Test 3: Create data processor
        print("3. Creating data processor...")
        processor = DataProcessor(config)
        print("   OK: Data processor created")
        
        # Test 4: Load data
        print("4. Loading sample data...")
        df = processor.load_data('sample_air_quality_data.csv')
        print(f"   OK: Data loaded - Shape: {df.shape}")
        
        # Test 5: Process data
        print("5. Processing data...")
        processed_data = processor.process_data(df)
        print(f"   OK: Data processed - Shape: {processed_data.shape}")
        
        print("\nSUCCESS: All tests passed!")
        print("If you're still getting errors, please run this script and share the output.")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        
        print("\nPlease copy this error message and share it for further assistance.")

if __name__ == "__main__":
    test_sample_data()
