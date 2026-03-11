#!/usr/bin/env python3
"""
Air Pollution Forecasting System
Main entry point for the optimized air quality prediction system

Author: Air Quality Commission
Created: 2026-02-25
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import Config
    from src.data_processor import DataProcessor
    from src.model_trainer import ModelTrainer
    from src.forecaster import Forecaster
    from src.visualizer import Visualizer
    from src.utils import setup_logging, PerformanceMonitor
    from src.guide_updater import GuideUpdater
except ImportError:
    from config import Config
    from data_processor import DataProcessor
    from model_trainer import ModelTrainer
    from forecaster import Forecaster
    from visualizer import Visualizer
    from utils import setup_logging, PerformanceMonitor
    try:
        from guide_updater import GuideUpdater
    except ImportError:
        GuideUpdater = None


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Air Pollution Forecasting System')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Configuration file path')
    parser.add_argument('--data', type=str, default='data/air_quality_data.csv',
                       help='Data file path')
    parser.add_argument('--output', type=str, default='outputs',
                       help='Output directory')
    parser.add_argument('--days', type=int, default=31,
                       help='Forecast horizon in days')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--update-guide', action='store_true',
                       help='Check and update USER_GUIDE.md before execution')
    parser.add_argument('--setup-guide', action='store_true',
                       help='Setup automatic guide update system')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("AIR POLLUTION FORECASTING SYSTEM")
    logger.info("=" * 80)
    
    # Handle guide update commands
    if GuideUpdater:
        if args.setup_guide:
            logger.info("Setting up automatic guide update system...")
            updater = GuideUpdater()
            updater.setup_auto_update()
            logger.info("Guide update system setup completed")
            return
        
        if args.update_guide:
            logger.info("Checking for guide updates...")
            updater = GuideUpdater()
            updated = updater.check_and_update()
            if updated:
                logger.info("USER_GUIDE.md has been updated")
            else:
                logger.info("USER_GUIDE.md is up to date")
    else:
        logger.warning("Guide updater not available - skipping guide updates")
    
    try:
        # Initialize configuration
        config = Config(args.config)
        
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        
        # Initialize performance monitor
        perf_monitor = PerformanceMonitor()
        
        # Data Processing
        logger.info("Step 1: Processing air quality data...")
        with perf_monitor.measure("data_processing"):
            data_processor = DataProcessor(config)
            df = data_processor.load_data(args.data)
            processed_data = data_processor.process_data(df)
        
        # Model Training
        logger.info("Step 2: Training forecasting models...")
        with perf_monitor.measure("model_training"):
            trainer = ModelTrainer(config)
            prophet_model = trainer.train_prophet(processed_data)
            arima_model = trainer.train_arima(processed_data)
        
        # Forecasting
        logger.info("Step 3: Generating forecasts...")
        with perf_monitor.measure("forecasting"):
            forecaster = Forecaster(config)
            forecasts = forecaster.generate_ensemble_forecast(
                prophet_model, arima_model, processed_data, args.days
            )
        
        # Visualization
        logger.info("Step 4: Creating visualizations...")
        with perf_monitor.measure("visualization"):
            visualizer = Visualizer(config, output_dir)
            visualizer.create_all_visualizations(
                processed_data, forecasts, prophet_model, arima_model
            )
        
        # Performance Summary
        logger.info("Step 5: Generating performance summary...")
        perf_summary = perf_monitor.get_summary()
        logger.info(f"Total execution time: {perf_summary['total_time']:.2f} seconds")
        
        # Save results
        results_file = output_dir / f"forecast_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        forecasts.to_csv(results_file, index=False)
        logger.info(f"Results saved to: {results_file}")
        
        logger.info("=" * 80)
        logger.info("SYSTEM EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"System execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
