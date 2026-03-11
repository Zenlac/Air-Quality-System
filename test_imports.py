#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports...")

try:
    # Test basic imports
    print("Testing basic imports...")
    import pandas as pd
    import numpy as np
    print("  pandas, numpy - OK")
    
    # Test ML imports
    print("Testing ML imports...")
    from prophet import Prophet
    from pmdarima import auto_arima
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    print("  prophet, pmdarima, sklearn - OK")
    
    # Test utility imports
    print("Testing utility imports...")
    import yaml
    import matplotlib.pyplot as plt
    import seaborn as sns
    print("  yaml, matplotlib, seaborn - OK")
    
    # Test our modules
    print("Testing our modules...")
    from config import Config
    from utils import setup_logging, PerformanceMonitor
    print("  config, utils - OK")
    
    from data_processor import DataProcessor
    from model_trainer import ModelTrainer
    from forecaster import Forecaster
    from visualizer import Visualizer
    print("  data_processor, model_trainer, forecaster, visualizer - OK")
    
    print("\nSUCCESS: All imports successful!")
    print("The system is ready to use.")
    
except ImportError as e:
    print(f"\nERROR: Import error: {e}")
    print("\nSolution:")
    print("Install missing dependencies with:")
    print("pip install -r requirements.txt")
    
except Exception as e:
    print(f"\nERROR: Unexpected error: {e}")
    print("Please check error and fix accordingly.")
