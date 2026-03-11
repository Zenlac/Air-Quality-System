#!/usr/bin/env python3
"""
Performance Comparison Script
Compares performance between standard and optimized versions

Author: Air Quality Commission
Created: 2026-03-06
"""

import time
import psutil
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import seaborn as sns

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class PerformanceBenchmark:
    """Performance benchmarking class"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process()
    
    def measure_memory_usage(self):
        """Measure current memory usage"""
        return self.process.memory_info().rss / 1024 / 1024  # MB
    
    def benchmark_data_processing(self, data_path, processor_class, config_path):
        """Benchmark data processing performance"""
        
        print(f"Benchmarking {processor_class.__name__}...")
        
        # Load config
        from config import Config
        config = Config(config_path)
        
        # Measure initial memory
        initial_memory = self.measure_memory_usage()
        
        # Load data
        start_time = time.time()
        df = pd.read_csv(data_path)
        load_time = time.time() - start_time
        load_memory = self.measure_memory_usage()
        
        # Process data
        start_time = time.time()
        processor = processor_class(config)
        processed_data = processor.process_data(df)
        process_time = time.time() - start_time
        process_memory = self.measure_memory_usage()
        
        # Clean up
        del df, processed_data, processor
        import gc
        gc.collect()
        
        final_memory = self.measure_memory_usage()
        
        return {
            'load_time': load_time,
            'process_time': process_time,
            'total_time': load_time + process_time,
            'initial_memory': initial_memory,
            'load_memory': load_memory,
            'process_memory': process_memory,
            'final_memory': final_memory,
            'peak_memory': max(load_memory, process_memory),
            'memory_increase': final_memory - initial_memory
        }
    
    def benchmark_model_training(self, data_path, trainer_classes, config_path):
        """Benchmark model training performance"""
        
        print("Benchmarking model training...")
        
        # Load config
        from config import Config
        config = Config(config_path)
        
        # Load and process data
        from data_processor import DataProcessor
        processor = DataProcessor(config)
        df = pd.read_csv(data_path)
        processed_data = processor.process_data(df)
        
        results = {}
        initial_memory = self.measure_memory_usage()
        
        for trainer_name, trainer_class in trainer_classes.items():
            print(f"  Training {trainer_name}...")
            
            start_time = time.time()
            start_memory = self.measure_memory_usage()
            
            try:
                trainer = trainer_class(config)
                model = trainer.train(processed_data)
                
                end_time = time.time()
                end_memory = self.measure_memory_usage()
                
                results[trainer_name] = {
                    'training_time': end_time - start_time,
                    'memory_usage': end_memory - start_memory,
                    'success': True
                }
                
                # Clean up
                del model, trainer
                gc.collect()
                
            except Exception as e:
                results[trainer_name] = {
                    'training_time': float('inf'),
                    'memory_usage': 0,
                    'success': False,
                    'error': str(e)
                }
        
        final_memory = self.measure_memory_usage()
        
        return {
            'models': results,
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'total_memory_increase': final_memory - initial_memory
        }
    
    def benchmark_startup_time(self, script_path):
        """Benchmark application startup time"""
        
        print(f"Benchmarking startup time for {script_path}...")
        
        start_time = time.time()
        initial_memory = self.measure_memory_usage()
        
        try:
            # Run script with timeout
            process = subprocess.Popen(
                [sys.executable, script_path, '--help'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for completion or timeout
            try:
                stdout, stderr = process.communicate(timeout=30)
                end_time = time.time()
                final_memory = self.measure_memory_usage()
                
                return {
                    'startup_time': end_time - start_time,
                    'memory_increase': final_memory - initial_memory,
                    'success': process.returncode == 0,
                    'stdout': stdout[:500],  # First 500 chars
                    'stderr': stderr[:500]
                }
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'startup_time': float('inf'),
                    'memory_increase': 0,
                    'success': False,
                    'error': 'Timeout'
                }
                
        except Exception as e:
            return {
                'startup_time': float('inf'),
                'memory_increase': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_full_benchmark(self):
        """Run complete performance benchmark"""
        
        print("🚀 Starting Performance Benchmark")
        print("=" * 60)
        
        data_path = 'csv_files/data_files/sample_air_quality_data.csv'
        config_path = 'config.yaml'
        optimized_config_path = 'config_optimized.yaml'
        
        # Check if data file exists
        if not os.path.exists(data_path):
            print(f"❌ Data file not found: {data_path}")
            return
        
        # Benchmark data processing
        print("\n📊 Data Processing Benchmark")
        print("-" * 30)
        
        try:
            from data_processor import DataProcessor
            from data_processor_optimized import OptimizedDataProcessor
            
            # Standard processor
            standard_results = self.benchmark_data_processing(
                data_path, DataProcessor, config_path
            )
            
            # Optimized processor
            optimized_results = self.benchmark_data_processing(
                data_path, OptimizedDataProcessor, optimized_config_path
            )
            
            self.results['data_processing'] = {
                'standard': standard_results,
                'optimized': optimized_results
            }
            
            # Print comparison
            print(f"Standard Processing:")
            print(f"  Time: {standard_results['total_time']:.2f}s")
            print(f"  Memory: {standard_results['memory_increase']:.1f}MB")
            
            print(f"Optimized Processing:")
            print(f"  Time: {optimized_results['total_time']:.2f}s")
            print(f"  Memory: {optimized_results['memory_increase']:.1f}MB")
            
            # Calculate improvements
            time_improvement = (standard_results['total_time'] - optimized_results['total_time']) / standard_results['total_time'] * 100
            memory_improvement = (standard_results['memory_increase'] - optimized_results['memory_increase']) / standard_results['memory_increase'] * 100
            
            print(f"Improvements:")
            print(f"  Time: {time_improvement:.1f}% faster")
            print(f"  Memory: {memory_improvement:.1f}% less")
            
        except Exception as e:
            print(f"❌ Data processing benchmark failed: {e}")
        
        # Benchmark model training
        print("\n🤖 Model Training Benchmark")
        print("-" * 30)
        
        try:
            from prophet_trainer import ProphetTrainer
            from arima_trainer import ARIMATrainer
            
            trainer_classes = {
                'Prophet': ProphetTrainer,
                'ARIMA': ARIMATrainer
            }
            
            training_results = self.benchmark_model_training(
                data_path, trainer_classes, config_path
            )
            
            self.results['model_training'] = training_results
            
            for model_name, results in training_results['models'].items():
                if results['success']:
                    print(f"{model_name}: {results['training_time']:.2f}s, {results['memory_usage']:.1f}MB")
                else:
                    print(f"{model_name}: Failed ({results.get('error', 'Unknown error')})")
            
        except Exception as e:
            print(f"❌ Model training benchmark failed: {e}")
        
        # Benchmark startup time
        print("\n🚀 Startup Time Benchmark")
        print("-" * 30)
        
        try:
            # Standard startup
            standard_startup = self.benchmark_startup_time('run_ui.py')
            
            # Optimized startup
            optimized_startup = self.benchmark_startup_time('run_ui_optimized.py')
            
            self.results['startup'] = {
                'standard': standard_startup,
                'optimized': optimized_startup
            }
            
            print(f"Standard Startup: {standard_startup['startup_time']:.2f}s")
            print(f"Optimized Startup: {optimized_startup['startup_time']:.2f}s")
            
            if standard_startup['success'] and optimized_startup['success']:
                improvement = (standard_startup['startup_time'] - optimized_startup['startup_time']) / standard_startup['startup_time'] * 100
                print(f"Improvement: {improvement:.1f}% faster")
            
        except Exception as e:
            print(f"❌ Startup benchmark failed: {e}")
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate performance report"""
        
        print("\n📋 Performance Report")
        print("=" * 60)
        
        if 'data_processing' in self.results:
            dp = self.results['data_processing']
            print("Data Processing:")
            print(f"  Standard: {dp['standard']['total_time']:.2f}s, {dp['standard']['memory_increase']:.1f}MB")
            print(f"  Optimized: {dp['optimized']['total_time']:.2f}s, {dp['optimized']['memory_increase']:.1f}MB")
            
            if dp['standard']['total_time'] > 0:
                time_improvement = (dp['standard']['total_time'] - dp['optimized']['total_time']) / dp['standard']['total_time'] * 100
                print(f"  Time Improvement: {time_improvement:.1f}%")
        
        if 'model_training' in self.results:
            mt = self.results['model_training']
            print("\nModel Training:")
            for model, results in mt['models'].items():
                if results['success']:
                    print(f"  {model}: {results['training_time']:.2f}s")
        
        if 'startup' in self.results:
            su = self.results['startup']
            print("\nStartup Time:")
            print(f"  Standard: {su['standard']['startup_time']:.2f}s")
            print(f"  Optimized: {su['optimized']['startup_time']:.2f}s")
            
            if su['standard']['success'] and su['optimized']['success']:
                improvement = (su['standard']['startup_time'] - su['optimized']['startup_time']) / su['standard']['startup_time'] * 100
                print(f"  Improvement: {improvement:.1f}%")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save benchmark results to file"""
        
        results_file = 'performance_results.json'
        
        try:
            import json
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Results saved to {results_file}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    """Main benchmark runner"""
    
    print("🏁 Performance Comparison Tool")
    print("This tool compares standard vs optimized versions")
    print()
    
    # Check system resources
    memory = psutil.virtual_memory()
    print(f"System Memory: {memory.total / 1024**3:.1f} GB")
    print(f"Available Memory: {memory.available / 1024**3:.1f} GB")
    print(f"CPU Cores: {psutil.cpu_count()}")
    print()
    
    # Run benchmark
    benchmark = PerformanceBenchmark()
    benchmark.run_full_benchmark()
    
    print("\n✅ Benchmark completed!")

if __name__ == "__main__":
    main()
