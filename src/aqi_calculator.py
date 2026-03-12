"""
AQI Calculator Module
Calculates Air Quality Index and AQI buckets based on pollutant concentrations

Supports multiple AQI standards:
- US EPA AQI standard
- India NAAQS AQI standard
- China MEP AQI standard

Author: Air Quality Commission
Created: 2026-03-12
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging

class AQICalculator:
    """Air Quality Index Calculator"""
    
    def __init__(self, standard: str = 'US_EPA'):
        """
        Initialize AQI Calculator
        
        Args:
            standard: AQI standard to use ('US_EPA', 'INDIA_NAAQS', 'CHINA_MEP')
        """
        self.standard = standard
        self.logger = logging.getLogger(__name__)
        
        # AQI breakpoints and concentrations for different standards
        self.breakpoints = self._get_breakpoints(standard)
        
        # Pollutant sub-index calculation functions
        self.sub_index_functions = {
            'PM2.5': self._calculate_pm25_sub_index,
            'PM10': self._calculate_pm10_sub_index,
            'NO2': self._calculate_no2_sub_index,
            'CO': self._calculate_co_sub_index,
            'SO2': self._calculate_so2_sub_index,
            'O3': self._calculate_o3_sub_index,
            'NH3': self._calculate_nh3_sub_index,
            'NO': self._calculate_no_sub_index,
            'NOx': self._calculate_nox_sub_index,
            'Benzene': self._calculate_benzene_sub_index,
            'Toluene': self._calculate_toluene_sub_index,
            'Xylene': self._calculate_xylene_sub_index
        }
    
    def _get_breakpoints(self, standard: str) -> Dict:
        """Get AQI breakpoints for the specified standard"""
        
        if standard == 'US_EPA':
            return {
                'PM2.5': {
                    'breakpoints': [(0, 12.0, 0, 50), (12.1, 35.4, 51, 100), 
                                  (35.5, 55.4, 101, 150), (55.5, 150.4, 151, 200),
                                  (150.5, 250.4, 201, 300), (250.5, 350.4, 301, 400),
                                  (350.5, 500.4, 401, 500)],
                    'unit': 'μg/m³'
                },
                'PM10': {
                    'breakpoints': [(0, 54, 0, 50), (55, 154, 51, 100),
                                  (155, 254, 101, 150), (255, 354, 151, 200),
                                  (355, 424, 201, 300), (425, 504, 301, 400),
                                  (505, 604, 401, 500)],
                    'unit': 'μg/m³'
                },
                'NO2': {
                    'breakpoints': [(0, 53, 0, 50), (54, 100, 51, 100),
                                  (101, 360, 101, 150), (361, 649, 151, 200),
                                  (650, 1249, 201, 300), (1250, 1649, 301, 400),
                                  (1650, 2049, 401, 500)],
                    'unit': 'ppb'
                },
                'CO': {
                    'breakpoints': [(0.0, 4.4, 0, 50), (4.5, 9.4, 51, 100),
                                  (9.5, 12.4, 101, 150), (12.5, 15.4, 151, 200),
                                  (15.5, 30.4, 201, 300), (30.5, 40.4, 301, 400),
                                  (40.5, 50.4, 401, 500)],
                    'unit': 'ppm'
                },
                'SO2': {
                    'breakpoints': [(0, 35, 0, 50), (36, 75, 51, 100),
                                  (76, 185, 101, 150), (186, 304, 151, 200),
                                  (305, 604, 201, 300), (605, 804, 301, 400),
                                  (805, 1004, 401, 500)],
                    'unit': 'ppb'
                },
                'O3': {
                    'breakpoints': [(0, 54, 0, 50), (55, 70, 51, 100),
                                  (71, 85, 101, 150), (86, 105, 151, 200),
                                  (106, 200, 201, 300), (201, 300, 301, 400),
                                  (301, 400, 401, 500)],
                    'unit': 'ppb'
                }
            }
        elif standard == 'INDIA_NAAQS':
            return {
                'PM2.5': {
                    'breakpoints': [(0, 30, 0, 50), (31, 60, 51, 100),
                                  (61, 90, 101, 150), (91, 120, 151, 200),
                                  (121, 250, 201, 300), (251, 350, 301, 400),
                                  (351, 500, 401, 500)],
                    'unit': 'μg/m³'
                },
                'PM10': {
                    'breakpoints': [(0, 50, 0, 50), (51, 100, 51, 100),
                                  (101, 250, 101, 150), (251, 350, 151, 200),
                                  (351, 430, 201, 300), (431, 500, 301, 400),
                                  (501, 600, 401, 500)],
                    'unit': 'μg/m³'
                },
                'NO2': {
                    'breakpoints': [(0, 40, 0, 50), (41, 80, 51, 100),
                                  (81, 180, 101, 150), (181, 280, 151, 200),
                                  (281, 400, 201, 300), (401, 800, 301, 400),
                                  (801, 1200, 401, 500)],
                    'unit': 'ppb'
                },
                'CO': {
                    'breakpoints': [(0, 1.0, 0, 50), (1.1, 2.0, 51, 100),
                                  (2.1, 3.0, 101, 150), (3.1, 4.0, 151, 200),
                                  (4.1, 10.0, 201, 300), (10.1, 17.0, 301, 400),
                                  (17.1, 35.0, 401, 500)],
                    'unit': 'ppm'
                },
                'SO2': {
                    'breakpoints': [(0, 40, 0, 50), (41, 80, 51, 100),
                                  (81, 380, 101, 150), (381, 800, 151, 200),
                                  (801, 1600, 201, 300), (1601, 2100, 301, 400),
                                  (2101, 2620, 401, 500)],
                    'unit': 'ppb'
                },
                'O3': {
                    'breakpoints': [(0, 50, 0, 50), (51, 100, 51, 100),
                                  (101, 168, 101, 150), (169, 208, 151, 200),
                                  (209, 748, 201, 300), (749, 1000, 301, 400),
                                  (1001, 1200, 401, 500)],
                    'unit': 'ppb'
                }
            }
        else:  # Default to US EPA
            return self._get_breakpoints('US_EPA')
    
    def _calculate_sub_index(self, concentration: float, pollutant: str) -> float:
        """
        Calculate AQI sub-index for a pollutant
        
        Args:
            concentration: Pollutant concentration
            pollutant: Pollutant name
            
        Returns:
            AQI sub-index value
        """
        if pollutant not in self.breakpoints:
            self.logger.warning(f"Pollutant {pollutant} not supported for AQI calculation")
            return 0.0
        
        if concentration < 0:
            self.logger.warning(f"Negative concentration for {pollutant}: {concentration}")
            return 0.0
        
        breakpoints = self.breakpoints[pollutant]['breakpoints']
        
        # Find the appropriate breakpoint
        for i, (c_low, c_high, aqi_low, aqi_high) in enumerate(breakpoints):
            if c_low <= concentration <= c_high:
                # Linear interpolation
                if c_high == c_low:  # Avoid division by zero
                    return aqi_low
                
                sub_index = ((aqi_high - aqi_low) / (c_high - c_low)) * (concentration - c_low) + aqi_low
                return round(sub_index, 1)
        
        # If concentration is above the highest breakpoint
        if concentration > breakpoints[-1][1]:
            return 500.0  # Maximum AQI value
        
        # If concentration is below the lowest breakpoint
        return 0.0
    
    def _calculate_pm25_sub_index(self, concentration: float) -> float:
        """Calculate PM2.5 sub-index"""
        return self._calculate_sub_index(concentration, 'PM2.5')
    
    def _calculate_pm10_sub_index(self, concentration: float) -> float:
        """Calculate PM10 sub-index"""
        return self._calculate_sub_index(concentration, 'PM10')
    
    def _calculate_no2_sub_index(self, concentration: float) -> float:
        """Calculate NO2 sub-index"""
        return self._calculate_sub_index(concentration, 'NO2')
    
    def _calculate_co_sub_index(self, concentration: float) -> float:
        """Calculate CO sub-index"""
        return self._calculate_sub_index(concentration, 'CO')
    
    def _calculate_so2_sub_index(self, concentration: float) -> float:
        """Calculate SO2 sub-index"""
        return self._calculate_sub_index(concentration, 'SO2')
    
    def _calculate_o3_sub_index(self, concentration: float) -> float:
        """Calculate O3 sub-index"""
        return self._calculate_sub_index(concentration, 'O3')
    
    def _calculate_nh3_sub_index(self, concentration: float) -> float:
        """Calculate NH3 sub-index (using PM2.5 breakpoints as reference)"""
        return self._calculate_sub_index(concentration, 'PM2.5')
    
    def _calculate_no_sub_index(self, concentration: float) -> float:
        """Calculate NO sub-index (using NO2 breakpoints as reference)"""
        return self._calculate_sub_index(concentration, 'NO2')
    
    def _calculate_nox_sub_index(self, concentration: float) -> float:
        """Calculate NOx sub-index (using NO2 breakpoints as reference)"""
        return self._calculate_sub_index(concentration, 'NO2')
    
    def _calculate_benzene_sub_index(self, concentration: float) -> float:
        """Calculate Benzene sub-index (using PM2.5 breakpoints as reference)"""
        return self._calculate_sub_index(concentration, 'PM2.5')
    
    def _calculate_toluene_sub_index(self, concentration: float) -> float:
        """Calculate Toluene sub-index (using PM2.5 breakpoints as reference)"""
        return self._calculate_sub_index(concentration, 'PM2.5')
    
    def _calculate_xylene_sub_index(self, concentration: float) -> float:
        """Calculate Xylene sub-index (using PM2.5 breakpoints as reference)"""
        return self._calculate_sub_index(concentration, 'PM2.5')
    
    def calculate_aqi(self, concentrations: Dict[str, float]) -> float:
        """
        Calculate overall AQI from pollutant concentrations
        
        Args:
            concentrations: Dictionary of pollutant concentrations
            
        Returns:
            Overall AQI value
        """
        sub_indices = {}
        
        for pollutant, concentration in concentrations.items():
            if pollutant in self.sub_index_functions and not pd.isna(concentration):
                try:
                    sub_index = self.sub_index_functions[pollutant](concentration)
                    sub_indices[pollutant] = sub_index
                except Exception as e:
                    self.logger.warning(f"Error calculating sub-index for {pollutant}: {e}")
                    continue
        
        if not sub_indices:
            self.logger.warning("No valid sub-indices calculated")
            return 0.0
        
        # Overall AQI is the maximum of all sub-indices
        overall_aqi = max(sub_indices.values())
        
        self.logger.debug(f"Sub-indices: {sub_indices}")
        self.logger.debug(f"Overall AQI: {overall_aqi}")
        
        return round(overall_aqi, 1)
    
    def get_aqi_bucket(self, aqi_value: float) -> Tuple[str, str, str]:
        """
        Get AQI bucket/category information
        
        Args:
            aqi_value: AQI value
            
        Returns:
            Tuple of (category, color, health_message)
        """
        if aqi_value <= 50:
            return "Good", "green", "Air quality is satisfactory"
        elif aqi_value <= 100:
            return "Moderate", "yellow", "Air quality is acceptable"
        elif aqi_value <= 150:
            return "Unhealthy for Sensitive Groups", "orange", "Members of sensitive groups may experience health effects"
        elif aqi_value <= 200:
            return "Unhealthy", "red", "Everyone may begin to experience health effects"
        elif aqi_value <= 300:
            return "Very Unhealthy", "purple", "Health warnings of emergency conditions"
        else:
            return "Hazardous", "maroon", "Health alert: everyone may experience serious health effects"
    
    def calculate_aqi_with_bucket(self, concentrations: Dict[str, float]) -> Dict[str, any]:
        """
        Calculate AQI and bucket information
        
        Args:
            concentrations: Dictionary of pollutant concentrations
            
        Returns:
            Dictionary with AQI value and bucket information
        """
        aqi_value = self.calculate_aqi(concentrations)
        category, color, health_message = self.get_aqi_bucket(aqi_value)
        
        return {
            'aqi_value': aqi_value,
            'category': category,
            'color': color,
            'health_message': health_message,
            'standard': self.standard
        }
    
    def calculate_aqi_for_dataframe(self, df: pd.DataFrame, 
                                  pollutant_columns: List[str] = None) -> pd.DataFrame:
        """
        Calculate AQI for all rows in a DataFrame
        
        Args:
            df: DataFrame with pollutant concentrations
            pollutant_columns: List of pollutant columns to use
            
        Returns:
            DataFrame with added AQI columns
        """
        if pollutant_columns is None:
            pollutant_columns = ['PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'O3', 'NH3', 'NO', 'NOx', 'Benzene', 'Toluene', 'Xylene']
        
        # Filter columns that exist in the DataFrame
        available_columns = [col for col in pollutant_columns if col in df.columns]
        
        if not available_columns:
            self.logger.warning("No pollutant columns found in DataFrame")
            return df
        
        # Calculate AQI for each row
        aqi_values = []
        categories = []
        colors = []
        health_messages = []
        
        for _, row in df.iterrows():
            concentrations = {}
            for col in available_columns:
                if not pd.isna(row[col]):
                    concentrations[col] = row[col]
            
            if concentrations:
                result = self.calculate_aqi_with_bucket(concentrations)
                aqi_values.append(result['aqi_value'])
                categories.append(result['category'])
                colors.append(result['color'])
                health_messages.append(result['health_message'])
            else:
                aqi_values.append(0.0)
                categories.append("Unknown")
                colors.append("gray")
                health_messages.append("Insufficient data")
        
        # Add AQI columns to DataFrame
        df_calculated = df.copy()
        df_calculated['Calculated_AQI'] = aqi_values
        df_calculated['AQI_Category'] = categories
        df_calculated['AQI_Color'] = colors
        df_calculated['Health_Message'] = health_messages
        
        return df_calculated
    
    def get_dominant_pollutant(self, concentrations: Dict[str, float]) -> Tuple[str, float]:
        """
        Get the dominant pollutant (highest sub-index)
        
        Args:
            concentrations: Dictionary of pollutant concentrations
            
        Returns:
            Tuple of (pollutant_name, sub_index_value)
        """
        sub_indices = {}
        
        for pollutant, concentration in concentrations.items():
            if pollutant in self.sub_index_functions and not pd.isna(concentration):
                try:
                    sub_index = self.sub_index_functions[pollutant](concentration)
                    sub_indices[pollutant] = sub_index
                except Exception as e:
                    self.logger.warning(f"Error calculating sub-index for {pollutant}: {e}")
                    continue
        
        if not sub_indices:
            return "Unknown", 0.0
        
        dominant_pollutant = max(sub_indices, key=sub_indices.get)
        return dominant_pollutant, sub_indices[dominant_pollutant]
    
    def get_aqi_statistics(self, df: pd.DataFrame, aqi_column: str = 'Calculated_AQI') -> Dict[str, any]:
        """
        Get AQI statistics for a DataFrame
        
        Args:
            df: DataFrame with AQI values
            aqi_column: Name of AQI column
            
        Returns:
            Dictionary with AQI statistics
        """
        if aqi_column not in df.columns:
            self.logger.warning(f"AQI column {aqi_column} not found")
            return {}
        
        aqi_values = df[aqi_column].dropna()
        
        if len(aqi_values) == 0:
            return {}
        
        return {
            'mean': aqi_values.mean(),
            'median': aqi_values.median(),
            'min': aqi_values.min(),
            'max': aqi_values.max(),
            'std': aqi_values.std(),
            'count': len(aqi_values),
            'category_distribution': aqi_values.apply(
                lambda x: self.get_aqi_bucket(x)[0]
            ).value_counts().to_dict()
        }

# Factory function for creating AQI calculator
def create_aqi_calculator(standard: str = 'US_EPA') -> AQICalculator:
    """Create AQI calculator instance"""
    return AQICalculator(standard)
