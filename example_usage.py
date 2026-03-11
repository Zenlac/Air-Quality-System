#!/usr/bin/env python3
"""
Example usage of the Air Pollution Forecasting System

This script demonstrates how to use the system programmatically
for different use cases and scenarios.

Author: Air Quality Commission
Created: 2026-02-25
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from src.forecaster import Forecaster
from src.visualizer import Visualizer
from src.utils import setup_logging, PerformanceMonitor


def create_sample_data():
    """Create sample air quality data for demonstration"""
    print("Creating sample air quality data...")
    
    # Create date range
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate synthetic AQI data with seasonal patterns
    np.random.seed(42)
    
    # Base AQI with seasonal variation
    base_aqi = 50 + 30 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
    
    # Add weekly pattern
    weekly_pattern = 10 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
    
    # Add random noise
    noise = np.random.normal(0, 15, len(dates))
    
    # Combine to create AQI values
    aqi_values = base_aqi + weekly_pattern + noise
    aqi_values = np.clip(aqi_values, 0, 500)  # Ensure valid AQI range
    
    # Create pollutant data (correlated with AQI)
    pm25 = aqi_values * np.random.uniform(0.3, 0.7, len(dates))
    pm10 = aqi_values * np.random.uniform(0.5, 1.2, len(dates))
    no2 = aqi_values * np.random.uniform(0.1, 0.4, len(dates))
    co = aqi_values * np.random.uniform(0.01, 0.1, len(dates))
    
    # Create DataFrame
    data = pd.DataFrame({
        'Timestamp': dates,
        'AQI': aqi_values,
        'PM2.5': pm25,
        'PM10': pm10,
        'NO2': no2,
        'CO': co,
        'NO': np.random.uniform(5, 50, len(dates)),
        'NOx': np.random.uniform(10, 80, len(dates)),
        'NH3': np.random.uniform(1, 20, len(dates)),
        'SO2': np.random.uniform(2, 30, len(dates)),
        'O3': np.random.uniform(10, 100, len(dates)),
        'Benzene': np.random.uniform(0.1, 5, len(dates)),
        'Toluene': np.random.uniform(0.5, 10, len(dates)),
        'Xylene': np.random.uniform(0.2, 8, len(dates))
    })
    
    # Add some missing values to make it realistic
    for col in ['PM2.5', 'PM10', 'NO2', 'CO']:
        missing_indices = np.random.choice(len(data), size=int(0.05 * len(data)), replace=False)
        data.loc[missing_indices, col] = np.nan
    
    return data


def example_basic_usage():
    """Example of basic system usage"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic System Usage")
    print("="*60)
    
    # Setup logging
    setup_logging(verbose=False)
    
    # Create sample data
    data = create_sample_data()
    data.to_csv('sample_air_quality_data.csv', index=False)
    
    # Initialize configuration
    config = Config('config.yaml')
    
    # Initialize system components
    processor = DataProcessor(config)
    trainer = ModelTrainer(config)
    forecaster = Forecaster(config)
    visualizer = Visualizer(config, 'example_outputs')
    
    # Process data
    print("Processing data...")
    processed_data = processor.process_data(data)
    
    # Train models
    print("Training models...")
    prophet_model = trainer.train_prophet(processed_data)
    arima_model = trainer.train_arima(processed_data)
    
    # Generate forecasts
    print("Generating forecasts...")
    forecasts = forecaster.generate_ensemble_forecast(
        prophet_model, arima_model, processed_data, horizon=31
    )
    
    # Create visualizations
    print("Creating visualizations...")
    visualizer.create_all_visualizations(
        processed_data, forecasts, prophet_model, arima_model
    )
    
    # Generate report
    report = forecaster.generate_forecast_report(forecasts)
    print("\nForecast Report:")
    print(report)
    
    print(f"\nResults saved to: example_outputs/")
    print(f"Sample data saved to: sample_air_quality_data.csv")


def example_custom_configuration():
    """Example of using custom configuration"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Configuration")
    print("="*60)
    
    # Create custom configuration
    config = Config()
    
    # Modify configuration
    config.set('forecasting.prophet_weight', 0.7)
    config.set('forecasting.arima_weight', 0.3)
    config.set('forecasting.default_horizon', 14)
    config.set('prophet.changepoint_prior_scale', 0.1)
    config.set('arima.max_p', 5)
    config.set('arima.max_q', 5)
    
    # Save custom configuration
    config.save_config()
    
    print("Custom configuration created:")
    print(f"Prophet weight: {config.get('forecasting.prophet_weight')}")
    print(f"ARIMA weight: {config.get('forecasting.arima_weight')}")
    print(f"Forecast horizon: {config.get('forecasting.default_horizon')}")
    print(f"Prophet changepoint scale: {config.get('prophet.changepoint_prior_scale')}")


def example_performance_monitoring():
    """Example of performance monitoring"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Performance Monitoring")
    print("="*60)
    
    # Initialize performance monitor
    perf_monitor = PerformanceMonitor()
    
    # Simulate some operations
    with perf_monitor.measure("data_loading"):
        import time
        time.sleep(0.5)  # Simulate data loading
    
    with perf_monitor.measure("model_training"):
        time.sleep(1.0)  # Simulate model training
    
    with perf_monitor.measure("forecasting"):
        time.sleep(0.3)  # Simulate forecasting
    
    # Get performance summary
    summary = perf_monitor.get_summary()
    
    print("Performance Summary:")
    print(f"Total time: {summary['total_time']:.2f} seconds")
    for operation, metrics in summary.items():
        if operation != 'total_time':
            print(f"{operation}: {metrics['average_time']:.3f}s (avg)")


def example_forecast_analysis():
    """Example of detailed forecast analysis"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Detailed Forecast Analysis")
    print("="*60)
    
    # Load and process data
    data = create_sample_data()
    config = Config('config.yaml')
    
    processor = DataProcessor(config)
    processed_data = processor.process_data(data)
    
    # Train models
    trainer = ModelTrainer(config)
    prophet_model = trainer.train_prophet(processed_data)
    arima_model = trainer.train_arima(processed_data)
    
    # Generate forecasts
    forecaster = Forecaster(config)
    forecasts = forecaster.generate_ensemble_forecast(
        prophet_model, arima_model, processed_data, horizon=31
    )
    
    # Analyze forecasts
    summary = forecaster.get_forecast_summary(forecasts)
    critical_periods = forecaster.identify_critical_periods(forecasts)
    
    print("Forecast Summary:")
    print(f"  Period: {summary['forecast_period']['start_date'].strftime('%Y-%m-%d')} to {summary['forecast_period']['end_date'].strftime('%Y-%m-%d')}")
    print(f"  Average AQI: {summary['aqi_statistics']['mean']:.2f}")
    print(f"  AQI Range: {summary['aqi_statistics']['min']:.2f} - {summary['aqi_statistics']['max']:.2f}")
    print(f"  Mean Confidence: {summary['confidence_statistics']['mean_confidence']:.3f}")
    
    print("\nAQI Category Distribution:")
    for category, count in summary['category_distribution'].items():
        percentage = (count / len(forecasts)) * 100
        print(f"  {category}: {count} days ({percentage:.1f}%)")
    
    print("\nHealth Impact:")
    print(f"  Good/Moderate days: {summary['health_impact']['good_days'] + summary['health_impact']['moderate_days']}")
    print(f"  Unhealthy days: {summary['health_impact']['unhealthy_days']}")
    print(f"  Hazardous days: {summary['health_impact']['hazardous_days']}")
    
    if len(critical_periods) > 0:
        print(f"\nCritical Periods (Top 5):")
        for date, row in critical_periods.head(5).iterrows():
            print(f"  {date.strftime('%Y-%m-%d')}: AQI {row['Forecasted_AQI']:.1f} ({row['AQI_Category']})")


def example_custom_visualization():
    """Example of creating custom visualizations"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Visualization")
    print("="*60)
    
    # Load and process data
    data = create_sample_data()
    config = Config('config.yaml')
    
    processor = DataProcessor(config)
    processed_data = processor.process_data(data)
    
    # Train models
    trainer = ModelTrainer(config)
    prophet_model = trainer.train_prophet(processed_data)
    arima_model = trainer.train_arima(processed_data)
    
    # Generate forecasts
    forecaster = Forecaster(config)
    forecasts = forecaster.generate_ensemble_forecast(
        prophet_model, arima_model, processed_data, horizon=31
    )
    
    # Create custom visualizations
    visualizer = Visualizer(config, 'custom_outputs')
    
    # Create individual plots
    visualizer.plot_historical_data(processed_data, 'custom_historical')
    visualizer.plot_ensemble_forecast(processed_data, forecasts, 'custom_ensemble')
    visualizer.plot_aqi_categories(forecasts, 'custom_categories')
    visualizer.create_forecast_dashboard(processed_data, forecasts, 'custom_dashboard')
    
    print("Custom visualizations created in: custom_outputs/")


def main():
    """Main function to run all examples"""
    print("Air Pollution Forecasting System - Example Usage")
    print("=" * 60)
    
    try:
        # Run examples
        example_basic_usage()
        example_custom_configuration()
        example_performance_monitoring()
        example_forecast_analysis()
        example_custom_visualization()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
