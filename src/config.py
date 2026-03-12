"""
Configuration Management Module
Handles system configuration and settings

Author: Air Quality Commission
Created: 2026-02-25
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the air pollution forecasting system"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            'data': {
                'date_column': 'Timestamp',
                'target_column': 'AQI',
                'pollutant_columns': [
                    'PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 
                    'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'
                ],
                'missing_threshold': 0.3,
                'outlier_threshold': 3.0
            },
            'prophet': {
                'yearly_seasonality': True,
                'weekly_seasonality': True,
                'daily_seasonality': False,
                'seasonality_mode': 'additive',
                'changepoint_prior_scale': 0.1,
                'seasonality_prior_scale': 5.0,
                'holidays_prior_scale': 5.0,
                'mcmc_samples': 0,
                'interval_width': 0.8,
                'uncertainty_samples': 500
            },
            'arima': {
                'start_p': 0,
                'start_q': 0,
                'max_p': 2,
                'max_q': 2,
                'max_d': 1,
                'start_P': 0,
                'start_Q': 0,
                'max_P': 1,
                'max_Q': 1,
                'max_D': 1,
                'max_order': 4,
                'seasonal': True,
                'm': 7,
                'stepwise': True,
                'suppress_warnings': True,
                'error_action': 'ignore',
                'trace': False,
                'information_criterion': 'aic',
                'alpha': 0.05,
                'test': 'kpss',
                'seasonal_test': 'ocsb'
            },
            'forecasting': {
                'default_horizon': 31,
                'prophet_weight': 0.6,
                'arima_weight': 0.4,
                'confidence_level': 0.95
            },
            'visualization': {
                'figure_size': [16, 12],
                'dpi': 100,
                'style': 'seaborn-v0_8',
                'color_palette': 'husl',
                'save_format': 'png',
                'bbox_inches': 'tight'
            },
            'performance': {
                'enable_monitoring': True,
                'memory_optimization': True,
                'parallel_processing': True,
                'cache_results': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'air_pollution_system.log'
            }
        }
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """Validate configuration values"""
        required_sections = ['data', 'prophet', 'arima', 'forecasting', 'visualization']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate data configuration
        data_config = self.config['data']
        if not data_config.get('target_column'):
            raise ValueError("Target column must be specified in data configuration")
        
        # Validate weights sum to 1
        prophet_weight = self.get('forecasting.prophet_weight', 0.6)
        arima_weight = self.get('forecasting.arima_weight', 0.4)
        if abs(prophet_weight + arima_weight - 1.0) > 0.01:
            raise ValueError("Prophet and ARIMA weights must sum to 1.0")
        
        return True
