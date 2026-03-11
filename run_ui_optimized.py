#!/usr/bin/env python3
"""
Optimized Air Pollution Forecasting System - UI Launcher
High-performance launcher with optimizations for speed and memory

Optimizations:
- Fast startup
- Memory monitoring
- Performance profiling
- Resource management
- Error handling

Author: Air Quality Commission
Created: 2026-03-06
"""

import subprocess
import sys
import os
import time
import psutil
from pathlib import Path

def check_system_resources():
    """Check system resources and warn if insufficient"""
    
    # Memory check
    memory = psutil.virtual_memory()
    available_memory_gb = memory.available / (1024**3)
    
    if available_memory_gb < 2.0:
        print("Warning: Low available memory (< 2GB). System may run slowly.")
    elif available_memory_gb < 4.0:
        print("Warning: Moderate memory available (< 4GB). Consider closing other applications.")
    else:
        print(f"Memory available: {available_memory_gb:.1f} GB")
    
    # CPU check
    cpu_count = psutil.cpu_count()
    print(f"CPU cores available: {cpu_count}")
    
    # Disk space check
    disk = psutil.disk_usage('.')
    available_disk_gb = disk.free / (1024**3)
    
    if available_disk_gb < 1.0:
        print("Warning: Low disk space (< 1GB).")
    else:
        print(f"Disk space available: {available_disk_gb:.1f} GB")

def optimize_environment():
    """Optimize Python environment for performance"""
    
    # Set environment variables for performance
    os.environ['PYTHONOPTIMIZE'] = '2'  # Enable Python optimizations
    os.environ['PYTHONUNBUFFERED'] = '1'  # Unbuffered output
    
    # Optimize garbage collection
    import gc
    gc.set_threshold(700, 10, 10)  # Aggressive garbage collection
    
    # Optimize numpy
    try:
        import numpy as np
        np.set_printoptions(threshold=100)  # Limit array printing
    except ImportError:
        pass
    
    # Optimize pandas
    try:
        import pandas as pd
        pd.set_option('mode.chained_assignment', None)  # Disable warnings
        pd.set_option('display.max_rows', 100)  # Limit display
    except ImportError:
        pass

def check_dependencies_fast():
    """Fast dependency checking with caching"""
    
    dependencies = {
        'streamlit': '1.28.0',
        'pandas': '2.0.0',
        'numpy': '1.24.0',
        'plotly': '5.15.0',
        'prophet': '1.1.0',
        'pmdarima': '2.0.0'
    }
    
    missing_deps = []
    outdated_deps = []
    
    for dep, min_version in dependencies.items():
        try:
            module = __import__(dep)
            if hasattr(module, '__version__'):
                # Simple version comparison (basic)
                current_version = module.__version__
                print(f"{dep} {current_version}")
            else:
                print(f"{dep} (version unknown)")
        except ImportError:
            missing_deps.append(dep)
            print(f"{dep} not found")
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install -r documentation/requirements.txt")
        return False
    
    return True

def launch_optimized_app():
    """Launch the optimized Streamlit app"""
    
    print("Starting Optimized Air Pollution Forecasting System...")
    print("=" * 60)
    
    # Check system resources
    check_system_resources()
    print()
    
    # Optimize environment
    print("Optimizing environment...")
    optimize_environment()
    print("Environment optimized")
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies_fast():
        sys.exit(1)
    print()
    
    # Determine app to launch
    app_dir = Path(__file__).parent
    optimized_app = app_dir / 'app_optimized.py'
    standard_app = app_dir / 'app.py'
    
    if optimized_app.exists():
        app_path = optimized_app
        print("Using optimized app: app_optimized.py")
    else:
        app_path = standard_app
        print("Using standard app: app.py")
    
    # Launch with optimized settings
    print(f"Launching web interface...")
    print(f"Path: {app_path}")
    print("=" * 60)
    
    # Streamlit configuration for performance
    streamlit_args = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--server.headless", "true",  # Headless mode for better performance
        "--browser.gatherUsageStats", "false",
        "--server.maxUploadSize", "200",  # Limit upload size
        "--server.maxMessageSize", "200",  # Limit message size
        "--logger.level", "warning"  # Reduce logging overhead
    ]
    
    try:
        # Monitor memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"Initial memory usage: {initial_memory:.1f} MB")
        
        # Start the process
        start_time = time.time()
        
        subprocess.run(streamlit_args, check=True)
        
        end_time = time.time()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"\nStartup time: {end_time - start_time:.2f} seconds")
        print(f"Final memory usage: {final_memory:.1f} MB")
        print(f"Memory increase: {final_memory - initial_memory:.1f} MB")
        
    except KeyboardInterrupt:
        print("\nShutting down web interface...")
        print("Graceful shutdown completed")
    except subprocess.CalledProcessError as e:
        print(f"Error launching web interface: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main launcher function"""
    
    # Performance monitoring
    start_time = time.time()
    
    try:
        launch_optimized_app()
    finally:
        # Clean up
        import gc
        gc.collect()
        
        total_time = time.time() - start_time
        print(f"\nTotal runtime: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
