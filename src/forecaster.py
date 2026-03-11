"""
Forecasting Module
Handles ensemble forecasting using Prophet and ARIMA models

Author: Air Quality Commission
Created: 2026-02-25
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, Any
from datetime import datetime, timedelta
from prophet import Prophet

try:
    from .config import Config
    from .utils import PerformanceMonitor, get_aqi_category, get_health_recommendation
except ImportError:
    from config import Config
    from utils import PerformanceMonitor, get_aqi_category, get_health_recommendation


class Forecaster:
    """Ensemble forecaster combining Prophet and ARIMA models"""
    
    def __init__(self, config: Config):
        """
        Initialize forecaster
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.perf_monitor = PerformanceMonitor()
        
        # Get configuration values
        self.target_column = config.get('data.target_column', 'AQI')
        self.prophet_weight = config.get('forecasting.prophet_weight', 0.6)
        self.arima_weight = config.get('forecasting.arima_weight', 0.4)
        self.confidence_level = config.get('forecasting.confidence_level', 0.95)
        self.default_horizon = config.get('forecasting.default_horizon', 31)
    
    def generate_ensemble_forecast(self, prophet_model: Prophet, arima_model, 
                                 df: pd.DataFrame, horizon: int = None) -> pd.DataFrame:
        """
        Generate ensemble forecast combining Prophet and ARIMA predictions
        
        Args:
            prophet_model: Trained Prophet model
            arima_model: Trained ARIMA model
            df: Historical data
            horizon: Forecast horizon in days
            
        Returns:
            DataFrame with ensemble forecasts
        """
        if horizon is None:
            horizon = self.default_horizon
        
        self.logger.info(f"Generating {horizon}-day ensemble forecast...")
        
        with self.perf_monitor.measure("ensemble_forecasting"):
            # Generate individual forecasts
            prophet_forecast = self._generate_prophet_forecast(prophet_model, horizon)
            arima_forecast, arima_conf_int = self._generate_arima_forecast(arima_model, horizon)
            
            # Create ensemble forecast
            ensemble_forecast = self._create_ensemble_forecast(
                prophet_forecast, arima_forecast, arima_conf_int, df
            )
            
            # Add AQI categories and health recommendations
            ensemble_forecast = self._add_aqi_categories(ensemble_forecast)
            
            self.logger.info("Ensemble forecast generation completed")
            
        return ensemble_forecast
    
    def _generate_prophet_forecast(self, model: Prophet, horizon: int) -> pd.DataFrame:
        """
        Generate Prophet forecast
        
        Args:
            model: Trained Prophet model
            horizon: Forecast horizon
            
        Returns:
            Prophet forecast DataFrame
        """
        # Create future dataframe
        future = model.make_future_dataframe(periods=horizon, include_history=False)
        
        # Generate forecast
        forecast = model.predict(future)
        
        return forecast
    
    def _generate_arima_forecast(self, model, horizon: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate ARIMA forecast
        
        Args:
            model: Trained ARIMA model
            horizon: Forecast horizon
            
        Returns:
            Tuple of (forecast, confidence_interval)
        """
        # Generate forecast with confidence intervals
        forecast, conf_int = model.predict(
            n_periods=horizon,
            return_conf_int=True,
            alpha=1 - self.confidence_level
        )
        
        return forecast, conf_int
    
    def _create_ensemble_forecast(self, prophet_forecast: pd.DataFrame, 
                                arima_forecast: np.ndarray, arima_conf_int: np.ndarray,
                                df: pd.DataFrame) -> pd.DataFrame:
        """
        Create ensemble forecast from individual model predictions
        
        Args:
            prophet_forecast: Prophet forecast DataFrame
            arima_forecast: ARIMA forecast array
            arima_conf_int: ARIMA confidence intervals
            df: Historical data
            
        Returns:
            Ensemble forecast DataFrame
        """
        # Get forecast dates
        last_date = df.index[-1]
        forecast_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=len(prophet_forecast),
            freq='D'
        )
        
        # Create ensemble forecast using weighted average
        ensemble_values = (
            self.prophet_weight * prophet_forecast['yhat'].values +
            self.arima_weight * arima_forecast
        )
        
        # Calculate ensemble confidence intervals
        ensemble_lower = (
            self.prophet_weight * prophet_forecast['yhat_lower'].values +
            self.arima_weight * arima_conf_int[:, 0]
        )
        
        ensemble_upper = (
            self.prophet_weight * prophet_forecast['yhat_upper'].values +
            self.arima_weight * arima_conf_int[:, 1]
        )
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Forecasted_AQI': ensemble_values,
            'Lower_Bound': ensemble_lower,
            'Upper_Bound': ensemble_upper,
            'Prophet_Forecast': prophet_forecast['yhat'].values,
            'ARIMA_Forecast': arima_forecast,
            'Prophet_Lower': prophet_forecast['yhat_lower'].values,
            'Prophet_Upper': prophet_forecast['yhat_upper'].values,
            'ARIMA_Lower': arima_conf_int[:, 0],
            'ARIMA_Upper': arima_conf_int[:, 1]
        })
        
        # Set Date as index
        forecast_df = forecast_df.set_index('Date')
        
        return forecast_df
    
    def _add_aqi_categories(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add AQI categories and health recommendations to forecast
        
        Args:
            forecast_df: Forecast DataFrame
            
        Returns:
            Enhanced forecast DataFrame
        """
        # Add AQI categories
        forecast_df['AQI_Category'] = forecast_df['Forecasted_AQI'].apply(get_aqi_category)
        
        # Add health recommendations
        forecast_df['Health_Recommendation'] = forecast_df['AQI_Category'].apply(get_health_recommendation)
        
        # Add risk level (1-6 scale)
        category_risk = {
            'Good': 1,
            'Moderate': 2,
            'Unhealthy for Sensitive Groups': 3,
            'Unhealthy': 4,
            'Very Unhealthy': 5,
            'Hazardous': 6
        }
        forecast_df['Risk_Level'] = forecast_df['AQI_Category'].map(category_risk)
        
        # Add forecast confidence score
        forecast_df['Confidence_Score'] = self._calculate_confidence_score(forecast_df)
        
        return forecast_df
    
    def _calculate_confidence_score(self, forecast_df: pd.DataFrame) -> np.ndarray:
        """
        Calculate confidence score for each forecast
        
        Args:
            forecast_df: Forecast DataFrame
            
        Returns:
            Array of confidence scores
        """
        # Calculate confidence based on prediction interval width
        interval_width = forecast_df['Upper_Bound'] - forecast_df['Lower_Bound']
        max_width = interval_width.max()
        
        # Normalize to 0-1 scale (higher is better)
        confidence_scores = 1 - (interval_width / max_width)
        
        return confidence_scores.values
    
    def get_forecast_summary(self, forecast_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics of the forecast
        
        Args:
            forecast_df: Forecast DataFrame
            
        Returns:
            Dictionary with forecast summary
        """
        summary = {
            'forecast_period': {
                'start_date': forecast_df.index.min(),
                'end_date': forecast_df.index.max(),
                'total_days': len(forecast_df)
            },
            'aqi_statistics': {
                'mean': forecast_df['Forecasted_AQI'].mean(),
                'median': forecast_df['Forecasted_AQI'].median(),
                'std': forecast_df['Forecasted_AQI'].std(),
                'min': forecast_df['Forecasted_AQI'].min(),
                'max': forecast_df['Forecasted_AQI'].max()
            },
            'category_distribution': forecast_df['AQI_Category'].value_counts().to_dict(),
            'risk_distribution': forecast_df['Risk_Level'].value_counts().to_dict(),
            'confidence_statistics': {
                'mean_confidence': forecast_df['Confidence_Score'].mean(),
                'min_confidence': forecast_df['Confidence_Score'].min(),
                'max_confidence': forecast_df['Confidence_Score'].max()
            },
            'health_impact': {
                'good_days': len(forecast_df[forecast_df['AQI_Category'] == 'Good']),
                'moderate_days': len(forecast_df[forecast_df['AQI_Category'] == 'Moderate']),
                'unhealthy_days': len(forecast_df[forecast_df['AQI_Category'].str.contains('Unhealthy')]),
                'hazardous_days': len(forecast_df[forecast_df['AQI_Category'] == 'Hazardous'])
            }
        }
        
        return summary
    
    def identify_critical_periods(self, forecast_df: pd.DataFrame, 
                               risk_threshold: int = 4) -> pd.DataFrame:
        """
        Identify periods with high pollution levels
        
        Args:
            forecast_df: Forecast DataFrame
            risk_threshold: Risk level threshold (4+ = Unhealthy)
            
        Returns:
            DataFrame with critical periods
        """
        critical_periods = forecast_df[forecast_df['Risk_Level'] >= risk_threshold].copy()
        
        if len(critical_periods) > 0:
            critical_periods = critical_periods.sort_values('Risk_Level', ascending=False)
        
        return critical_periods
    
    def generate_forecast_report(self, forecast_df: pd.DataFrame) -> str:
        """
        Generate text report of the forecast
        
        Args:
            forecast_df: Forecast DataFrame
            
        Returns:
            Forecast report string
        """
        summary = self.get_forecast_summary(forecast_df)
        critical_periods = self.identify_critical_periods(forecast_df)
        
        report = []
        report.append("=" * 80)
        report.append("AIR POLLUTION FORECAST REPORT")
        report.append("=" * 80)
        report.append(f"Forecast Period: {summary['forecast_period']['start_date'].strftime('%Y-%m-%d')} to {summary['forecast_period']['end_date'].strftime('%Y-%m-%d')}")
        report.append(f"Total Days: {summary['forecast_period']['total_days']}")
        report.append("")
        
        report.append("AQI FORECAST SUMMARY:")
        report.append(f"  Average AQI: {summary['aqi_statistics']['mean']:.2f}")
        report.append(f"  Range: {summary['aqi_statistics']['min']:.2f} - {summary['aqi_statistics']['max']:.2f}")
        report.append("")
        
        report.append("AIR QUALITY DISTRIBUTION:")
        for category, count in summary['category_distribution'].items():
            percentage = (count / len(forecast_df)) * 100
            report.append(f"  {category}: {count} days ({percentage:.1f}%)")
        report.append("")
        
        report.append("HEALTH IMPACT SUMMARY:")
        report.append(f"  Good/Moderate days: {summary['health_impact']['good_days'] + summary['health_impact']['moderate_days']}")
        report.append(f"  Unhealthy days: {summary['health_impact']['unhealthy_days']}")
        report.append(f"  Hazardous days: {summary['health_impact']['hazardous_days']}")
        report.append("")
        
        if len(critical_periods) > 0:
            report.append("CRITICAL PERIODS (High Pollution):")
            for date, row in critical_periods.head(5).iterrows():
                report.append(f"  {date.strftime('%Y-%m-%d')}: AQI {row['Forecasted_AQI']:.1f} ({row['AQI_Category']})")
            report.append("")
        
        report.append("RECOMMENDATIONS:")
        if summary['health_impact']['unhealthy_days'] > 0:
            report.append("  - Plan outdoor activities carefully during unhealthy periods")
            report.append("  - Consider using air purifiers indoors")
        if summary['health_impact']['hazardous_days'] > 0:
            report.append("  - Avoid all outdoor activities during hazardous periods")
            report.append("  - Keep windows and doors closed")
        if summary['health_impact']['good_days'] + summary['health_impact']['moderate_days'] > len(forecast_df) * 0.7:
            report.append("  - Generally good air quality expected")
            report.append("  - Good time for outdoor activities")
        
        report.append("=" * 80)
        
        return "\n".join(report)
