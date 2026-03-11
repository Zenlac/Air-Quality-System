"""
Utility Functions Module
Common utilities for the air pollution forecasting system

Author: Air Quality Commission
Created: 2026-02-25
"""

import logging
import time
import functools
from contextlib import contextmanager
from typing import Dict, Any, Callable
from datetime import datetime


def setup_logging(verbose: bool = False, log_file: str = None):
    """
    Setup logging configuration
    
    Args:
        verbose: Enable verbose logging
        log_file: Log file path
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_aqi_category(aqi_value: float) -> str:
    """
    Get AQI category based on AQI value
    
    Args:
        aqi_value: AQI value
        
    Returns:
        AQI category string
    """
    if aqi_value <= 50:
        return 'Good'
    elif aqi_value <= 100:
        return 'Moderate'
    elif aqi_value <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif aqi_value <= 200:
        return 'Unhealthy'
    elif aqi_value <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'


def get_health_recommendation(aqi_category: str) -> str:
    """
    Get health recommendation based on AQI category
    
    Args:
        aqi_category: AQI category
        
    Returns:
        Health recommendation string
    """
    recommendations = {
        'Good': 'Air quality is satisfactory. Enjoy outdoor activities!',
        'Moderate': 'Unusually sensitive people should consider reducing prolonged outdoor exertion.',
        'Unhealthy for Sensitive Groups': 'People with heart/lung disease, older adults, and children should reduce prolonged outdoor exertion.',
        'Unhealthy': 'Everyone should reduce prolonged outdoor exertion. Sensitive groups should avoid outdoor activities.',
        'Very Unhealthy': 'Everyone should avoid prolonged outdoor exertion. Sensitive groups should remain indoors.',
        'Hazardous': 'Everyone should avoid outdoor activities. Remain indoors and keep windows closed.'
    }
    
    return recommendations.get(aqi_category, 'No specific recommendation')


def get_aqi_color(category: str) -> str:
    """
    Get color associated with AQI category
    
    Args:
        category: AQI category
        
    Returns:
        Color string
    """
    colors = {
        'Good': 'green',
        'Moderate': 'yellow',
        'Unhealthy for Sensitive Groups': 'orange',
        'Unhealthy': 'red',
        'Very Unhealthy': 'purple',
        'Hazardous': 'maroon'
    }
    
    return colors.get(category, 'gray')


class PerformanceMonitor:
    """Performance monitoring utility"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    @contextmanager
    def measure(self, operation_name: str):
        """
        Context manager to measure execution time
        
        Args:
            operation_name: Name of the operation being measured
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            self.add_metric(operation_name, execution_time)
    
    def measure_decorator(self, operation_name: str):
        """
        Decorator to measure execution time
        
        Args:
            operation_name: Name of the operation being measured
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    self.add_metric(operation_name, execution_time)
            return wrapper
        return decorator
    
    def start_timer(self, operation_name: str):
        """Start timing an operation"""
        self.start_times[operation_name] = time.time()
    
    def end_timer(self, operation_name: str) -> float:
        """End timing an operation and return duration"""
        if operation_name in self.start_times:
            end_time = time.time()
            duration = end_time - self.start_times[operation_name]
            self.add_metric(operation_name, duration)
            del self.start_times[operation_name]
            return duration
        return 0.0
    
    def add_metric(self, operation_name: str, duration: float):
        """Add a performance metric"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        self.metrics[operation_name].append(duration)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        total_time = 0.0
        
        for operation, times in self.metrics.items():
            if times:
                avg_time = sum(times) / len(times)
                total_time += avg_time
                summary[operation] = {
                    'count': len(times),
                    'total_time': sum(times),
                    'average_time': avg_time,
                    'min_time': min(times),
                    'max_time': max(times)
                }
        
        summary['total_time'] = total_time
        return summary
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.start_times.clear()


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate date range
    
    Args:
        start_date: Start date string
        end_date: End date string
        
    Returns:
        True if valid, False otherwise
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return start <= end
    except ValueError:
        return False


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division that returns default value if denominator is zero
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if denominator is zero
        
    Returns:
        Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def create_directory_if_not_exists(directory_path: str):
    """
    Create directory if it doesn't exist
    
    Args:
        directory_path: Path to directory
    """
    import os
    os.makedirs(directory_path, exist_ok=True)


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in MB
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    import os
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    return 0.0


def memory_usage_mb() -> float:
    """
    Get current memory usage in MB
    
    Returns:
        Memory usage in MB
    """
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0


def log_system_info(logger: logging.Logger):
    """
    Log system information
    
    Args:
        logger: Logger instance
    """
    import platform
    import sys
    
    logger.info("System Information:")
    logger.info(f"  Platform: {platform.platform()}")
    logger.info(f"  Python Version: {sys.version}")
    logger.info(f"  Memory Usage: {memory_usage_mb():.2f} MB")
