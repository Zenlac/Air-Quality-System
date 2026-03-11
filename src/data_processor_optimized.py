"""
Optimized Data Processor for Air Pollution Forecasting System

Optimizations:
- Vectorized operations
- Memory-efficient data types
- Parallel processing
- Lazy evaluation
- Efficient memory management
- Optimized datetime handling

Author: Air Quality Commission
Created: 2026-03-06
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import gc
from functools import lru_cache

class OptimizedDataProcessor:
    """Optimized data processor with performance improvements"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize optimized data processor"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get configuration values
        self.date_column = config.get('data.date_column', 'Timestamp')
        self.target_column = config.get('data.target_column', 'AQI')
        self.pollutant_columns = config.get('data.pollutant_columns', [])
        self.missing_threshold = config.get('data.missing_threshold', 0.3)
        self.outlier_threshold = config.get('data.outlier_threshold', 3.0)
        
        # Optimized data types
        self.dtype_mapping = {
            'Timestamp': 'datetime64[ns]',
            'AQI': 'float32',
            'PM2.5': 'float32',
            'PM10': 'float32',
            'NO2': 'float32',
            'CO': 'float32',
            'NO': 'float32',
            'NOx': 'float32',
            'NH3': 'float32',
            'SO2': 'float32',
            'O3': 'float32',
            'Benzene': 'float32',
            'Toluene': 'float32',
            'Xylene': 'float32'
        }
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data with optimized memory usage
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Loaded DataFrame with optimized data types
        """
        self.logger.info(f"Loading data from: {file_path}")
        
        # Define required columns
        required_columns = {
            'Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 
            'NH3', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'
        }
        
        # Load with optimized data types
        dtype_dict = {col: 'float32' for col in required_columns if col != 'Timestamp'}
        dtype_dict['Timestamp'] = 'str'
        
        # Read data in chunks for large files
        try:
            # First, read just the header to validate columns
            df_temp = pd.read_csv(file_path, nrows=1)
            available_columns = set(df_temp.columns.tolist())
            
            # Validate columns
            missing_columns = required_columns - available_columns
            if missing_columns:
                error_msg = f"Missing required columns: {sorted(missing_columns)}"
                error_msg += f"\nRequired: {sorted(required_columns)}"
                error_msg += f"\nAvailable: {sorted(available_columns)}"
                raise ValueError(error_msg)
            
            # Load full data with optimized types
            df = pd.read_csv(
                file_path,
                dtype=dtype_dict,
                parse_dates=['Timestamp'],
                infer_datetime_format=True
            )
            
            # Optimize memory usage
            df = self._optimize_memory_usage(df)
            
            self.logger.info(f"Data loaded successfully: {df.shape}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data with optimized operations
        
        Args:
            df: Input DataFrame
            
        Returns:
            Processed DataFrame
        """
        self.logger.info(f"Processing data: {df.shape}")
        
        # Create a copy to avoid modifying original
        processed_df = df.copy()
        
        # Optimized processing pipeline
        processed_df = self._process_datetime_optimized(processed_df)
        processed_df = self._handle_missing_values_optimized(processed_df)
        processed_df = self._remove_outliers_optimized(processed_df)
        processed_df = self._create_features_optimized(processed_df)
        processed_df = self._optimize_memory_usage(processed_df)
        
        # Clean up memory
        gc.collect()
        
        self.logger.info(f"Data processing completed: {processed_df.shape}")
        return processed_df
    
    def _optimize_memory_usage(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize memory usage by converting to appropriate data types"""
        
        # Convert numeric columns to float32
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Convert int columns to smallest possible type
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        # Convert object columns to category if they have low cardinality
        for col in df.select_dtypes(include=['object']).columns:
            if col != 'Timestamp':  # Don't convert timestamp
                unique_count = df[col].nunique()
                if unique_count / len(df) < 0.5:  # Less than 50% unique values
                    df[col] = df[col].astype('category')
        
        return df
    
    def _process_datetime_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimized datetime processing"""
        
        if self.date_column in df.columns:
            # Convert to datetime if not already
            if df[self.date_column].dtype != 'datetime64[ns]':
                df[self.date_column] = pd.to_datetime(df[self.date_column], infer_datetime_format=True)
            
            # Set as index and sort
            df = df.set_index(self.date_column)
            df = df.sort_index()
        
        return df
    
    def _handle_missing_values_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimized missing value handling"""
        
        # Handle zero AQI values (treat as missing)
        if self.target_column in df.columns:
            zero_mask = df[self.target_column] == 0
            zero_count = zero_mask.sum()
            if zero_count > 0:
                self.logger.warning(f"Found {zero_count} zero AQI values - treating as missing")
                df.loc[zero_mask, self.target_column] = np.nan
        
        # Vectorized missing value percentage calculation
        missing_percentages = df.isnull().mean()
        
        # Remove columns with too many missing values
        columns_to_keep = missing_percentages[missing_percentages <= self.missing_threshold].index
        df = df[columns_to_keep]
        
        # Fill missing values for target column
        if self.target_column in df.columns:
            # Use median for robust filling
            median_value = df[self.target_column].median()
            df[self.target_column] = df[self.target_column].fillna(median_value)
        
        # Vectorized filling for pollutant columns
        for col in self.pollutant_columns:
            if col in df.columns:
                median_value = df[col].median()
                df[col] = df[col].fillna(median_value)
        
        # Remove rows with missing target values
        df = df.dropna(subset=[self.target_column])
        
        return df
    
    def _remove_outliers_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimized outlier removal using vectorized operations"""
        
        if self.target_column in df.columns:
            # Calculate z-scores vectorized
            mean_val = df[self.target_column].mean()
            std_val = df[self.target_column].std()
            
            if std_val > 0:
                z_scores = np.abs((df[self.target_column] - mean_val) / std_val)
                outlier_mask = z_scores > self.outlier_threshold
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0:
                    self.logger.warning(f"Removing {outlier_count} outliers")
                    df = df[~outlier_mask]
        
        return df
    
    def _create_features_optimized(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimized feature creation using vectorized operations"""
        
        # Ensure index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            return df
        
        # Vectorized feature creation
        features = pd.DataFrame(index=df.index)
        
        # Time-based features (vectorized)
        features['day_of_week'] = df.index.dayofweek.astype('int8')
        features['month'] = df.index.month.astype('int8')
        features['year'] = df.index.year.astype('int16')
        features['day_of_year'] = df.index.dayofyear.astype('int16')
        
        # Season (vectorized)
        features['season'] = ((df.index.month % 12) // 3 + 1).astype('int8')
        
        # Weekend (vectorized)
        features['is_weekend'] = (df.index.dayofweek >= 5).astype('int8')
        
        # Concatenate features
        df = pd.concat([df, features], axis=1)
        
        return df
    
    @lru_cache(maxsize=128)
    def _get_pollutant_stats(self, data_hash: str) -> Dict[str, float]:
        """Cache pollutant statistics for performance"""
        # This would be implemented based on specific needs
        return {}
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get optimized data summary"""
        
        summary = {
            'shape': df.shape,
            'columns': list(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'date_range': None,
            'target_stats': {},
            'missing_values': {},
            'data_types': df.dtypes.to_dict()
        }
        
        # Date range
        if isinstance(df.index, pd.DatetimeIndex):
            summary['date_range'] = {
                'start': df.index.min().strftime('%Y-%m-%d'),
                'end': df.index.max().strftime('%Y-%m-%d'),
                'days': (df.index.max() - df.index.min()).days
            }
        
        # Target column statistics
        if self.target_column in df.columns:
            target_series = df[self.target_column]
            summary['target_stats'] = {
                'count': len(target_series),
                'mean': float(target_series.mean()),
                'std': float(target_series.std()),
                'min': float(target_series.min()),
                'max': float(target_series.max()),
                'median': float(target_series.median()),
                'zeros': int((target_series == 0).sum()),
                'missing': int(target_series.isnull().sum())
            }
        
        # Missing values
        missing_counts = df.isnull().sum()
        summary['missing_values'] = {
            col: int(count) for col, count in missing_counts.items() if count > 0
        }
        
        return summary

# Factory function for creating optimized processor
def create_optimized_processor(config: Dict[str, Any]) -> OptimizedDataProcessor:
    """Create optimized data processor instance"""
    return OptimizedDataProcessor(config)
