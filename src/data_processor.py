"""
Data Processing Module
Handles data loading, cleaning, and preprocessing

Author: Air Quality Commission
Created: 2026-02-25
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime

try:
    from .config import Config
    from .utils import PerformanceMonitor
except ImportError:
    from config import Config
    from utils import PerformanceMonitor


class DataProcessor:
    """Data processor for air quality data"""
    
    def __init__(self, config: Config):
        """
        Initialize data processor
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.perf_monitor = PerformanceMonitor()
        
        # Get configuration values
        self.date_column = config.get('data.date_column', 'Timestamp')
        self.target_column = config.get('data.target_column', 'AQI')
        self.pollutant_columns = config.get('data.pollutant_columns', [])
        self.missing_threshold = config.get('data.missing_threshold', 0.3)
        self.outlier_threshold = config.get('data.outlier_threshold', 3.0)
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from CSV file with strict format validation
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Loaded DataFrame
            
        Raises:
            ValueError: If data format doesn't match required structure
        """
        self.logger.info(f"Loading data from: {file_path}")
        
        try:
            # Define required columns based on sample_air_quality_data.csv format
            required_columns = {
                'Timestamp',  # Date column
                'AQI',        # Target column
                'PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 'NH3', 'SO2', 'O3', 
                'Benzene', 'Toluene', 'Xylene'  # Pollutant columns
            }
            
            # First load without date parsing to validate columns
            df_temp = pd.read_csv(file_path, nrows=1)
            available_columns = set(df_temp.columns.tolist())
            
            # Strict validation - all required columns must be present
            missing_columns = required_columns - available_columns
            if missing_columns:
                error_msg = f"Data format validation failed. Missing required columns: {sorted(missing_columns)}"
                error_msg += f"\nRequired columns: {sorted(required_columns)}"
                error_msg += f"\nAvailable columns: {sorted(available_columns)}"
                error_msg += f"\n\nPlease ensure your data file matches the format of sample_air_quality_data.csv"
                raise ValueError(error_msg)
            
            # Check for extra columns (optional - warn but don't fail)
            extra_columns = available_columns - required_columns
            if extra_columns:
                self.logger.warning(f"Extra columns found (will be ignored): {sorted(extra_columns)}")
            
            # Load data with strict validation
            df = pd.read_csv(
                file_path,
                parse_dates=['Timestamp'],  # Fixed column name
                dtype={
                    'AQI': np.float32,
                    'PM2.5': np.float32, 'PM10': np.float32, 'NO2': np.float32, 
                    'CO': np.float32, 'NO': np.float32, 'NOx': np.float32,
                    'NH3': np.float32, 'SO2': np.float32, 'O3': np.float32,
                    'Benzene': np.float32, 'Toluene': np.float32, 'Xylene': np.float32
                },
                low_memory=True
            )
            
            # Validate Timestamp format
            if not pd.api.types.is_datetime64_any_dtype(df['Timestamp']):
                self.logger.error("Timestamp column contains invalid date format")
                raise ValueError("Timestamp column must contain valid datetime values")
            
            # Validate AQI column has values
            if df['AQI'].isna().all():
                raise ValueError("AQI column cannot be empty. Please provide valid AQI values.")
            
            # Validate data has minimum rows
            if len(df) < 30:
                self.logger.warning(f"Dataset has only {len(df)} rows. Minimum 30 rows recommended for reliable forecasting.")
            
            self.logger.info(f"Data loaded and validated successfully. Shape: {df.shape}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and clean the data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Processed DataFrame
        """
        self.logger.info("Starting data processing...")
        
        with self.perf_monitor.measure("data_processing"):
            # Make a copy to avoid modifying original
            processed_df = df.copy()
            
            # Convert date column to datetime and set as index
            processed_df = self._process_datetime(processed_df)
            
            # Handle missing values
            processed_df = self._handle_missing_values(processed_df)
            
            # Remove outliers
            processed_df = self._remove_outliers(processed_df)
            
            # Add time-based features
            processed_df = self._add_time_features(processed_df)
            
            # Optimize memory usage
            processed_df = self._optimize_memory(processed_df)
            
            self.logger.info(f"Data processing completed. Final shape: {processed_df.shape}")
            
        return processed_df
    
    def _process_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process datetime column and set as index"""
        # Use fixed column name 'Timestamp' as required by format
        date_column = 'Timestamp'
        
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            df = df.set_index(date_column)
            df = df.sort_index()
        else:
            # This should never happen due to validation in load_data
            raise ValueError(f"Required column '{date_column}' not found in data")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        # Define fixed pollutant columns based on required format
        pollutant_columns = ['PM2.5', 'PM10', 'NO2', 'CO', 'NO', 'NOx', 'NH3', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
        target_column = 'AQI'
        
        # Check missing value percentages
        missing_percentages = df.isnull().sum() / len(df)
        
        # Remove columns with too many missing values
        columns_to_keep = missing_percentages[missing_percentages <= self.missing_threshold].index
        df = df[columns_to_keep]
        
        # Handle zero AQI values (treat as missing)
        if target_column in df.columns:
            zero_count = (df[target_column] == 0).sum()
            if zero_count > 0:
                self.logger.warning(f"Found {zero_count} zero AQI values - treating as missing and filling with median")
                # Replace zeros with NaN for proper handling
                df[target_column] = df[target_column].replace(0, np.nan)
        
        # Fill missing values for target column using median then forward/backward fill
        if target_column in df.columns:
            # Use median for robust filling (less affected by outliers)
            median_value = df[target_column].median()
            df[target_column] = df[target_column].fillna(median_value)
            df[target_column] = df[target_column].ffill().bfill()
        
        # Fill missing values for pollutant columns
        for col in pollutant_columns:
            if col in df.columns:
                df[col] = df[col].ffill().bfill()
        
        # Remove any remaining rows with missing target values
        df = df.dropna(subset=[target_column])
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers using z-score method"""
        target_column = 'AQI'
        
        if target_column in df.columns:
            # Calculate z-scores
            z_scores = np.abs((df[target_column] - df[target_column].mean()) / df[target_column].std())
            
            # Remove outliers
            outlier_mask = z_scores <= self.outlier_threshold
            original_count = len(df)
            df = df[outlier_mask]
            removed_count = original_count - len(df)
            
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} outliers from {target_column}")
        
        return df
    
    def _calculate_aqi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate AQI from pollutant concentrations
        
        Args:
            df: DataFrame with pollutant concentrations
            
        Returns:
            DataFrame with AQI column added
        """
        target_column = 'AQI'
        
        # AQI breakpoints for PM2.5 (US EPA standard)
        aqi_breakpoints = {
            'PM2.5': {
                'concentration': [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5],
                'aqi': [0, 51, 101, 151, 201, 301, 401, 500]
            },
            'PM10': {
                'concentration': [0, 55, 155, 255, 355, 425, 505, 605],
                'aqi': [0, 51, 101, 151, 201, 301, 401, 500]
            }
        }
        
        def calculate_sub_aqi(concentration, breakpoints):
            """Calculate AQI for a single pollutant"""
            if concentration <= 0:
                return 0
            
            for i in range(len(breakpoints['concentration']) - 1):
                if (breakpoints['concentration'][i] < concentration <= breakpoints['concentration'][i + 1]):
                    c_low = breakpoints['concentration'][i]
                    c_high = breakpoints['concentration'][i + 1]
                    i_low = breakpoints['aqi'][i]
                    i_high = breakpoints['aqi'][i + 1]
                    
                    return ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
            
            return 500  # Hazardous
        
        # Calculate AQI for each pollutant
        aqi_values = []
        for _, row in df.iterrows():
            max_aqi = 0
            for pollutant in ['PM2.5', 'PM10']:
                if pollutant in df.columns and pollutant in aqi_breakpoints:
                    aqi = calculate_sub_aqi(row[pollutant], aqi_breakpoints[pollutant])
                    max_aqi = max(max_aqi, aqi)
            aqi_values.append(max_aqi)
        
        df[target_column] = aqi_values
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features for better forecasting"""
        # Add day of week
        df['day_of_week'] = df.index.dayofweek
        
        # Add month
        df['month'] = df.index.month
        
        # Add season
        df['season'] = df.index.month % 12 // 3 + 1
        
        # Add year
        df['year'] = df.index.year
        
        # Add day of year
        df['day_of_year'] = df.index.dayofyear
        
        # Add weekend indicator
        df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
        
        return df
    
    def _optimize_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize memory usage by converting data types"""
        # Convert numeric columns to appropriate types
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary statistics of the processed data"""
        target_column = 'AQI'
        
        summary = {
            'shape': df.shape,
            'date_range': {
                'start': df.index.min(),
                'end': df.index.max(),
                'days': (df.index.max() - df.index.min()).days
            },
            'target_stats': {
                'mean': df[target_column].mean(),
                'std': df[target_column].std(),
                'min': df[target_column].min(),
                'max': df[target_column].max()
            },
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict()
        }
        
        return summary
