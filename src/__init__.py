"""
Air Pollution Forecasting System
A comprehensive system for air quality prediction using ensemble methods

Author: Air Quality Commission
Created: 2026-02-25
"""

__version__ = "1.0.0"
__author__ = "Air Quality Commission"
__email__ = "info@airquality.gov"

# Import main classes
from .config import Config
from .data_processor import DataProcessor
from .model_trainer import ModelTrainer
from .forecaster import Forecaster
from .visualizer import Visualizer
from .utils import setup_logging, PerformanceMonitor

__all__ = [
    'Config',
    'DataProcessor', 
    'ModelTrainer',
    'Forecaster',
    'Visualizer',
    'setup_logging',
    'PerformanceMonitor'
]
