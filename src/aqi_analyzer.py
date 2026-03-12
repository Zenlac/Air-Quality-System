"""
AQI Analyzer Module
Provides comprehensive AQI analysis and reporting functionality

Author: Air Quality Commission
Created: 2026-03-12
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

from aqi_calculator import AQICalculator, create_aqi_calculator

class AQIAnalyzer:
    """AQI Analysis and Reporting Class"""
    
    def __init__(self, standard: str = 'US_EPA'):
        """
        Initialize AQI Analyzer
        
        Args:
            standard: AQI standard to use ('US_EPA', 'INDIA_NAAQS', 'CHINA_MEP')
        """
        self.standard = standard
        self.calculator = create_aqi_calculator(standard)
        self.logger = logging.getLogger(__name__)
        
        # AQI categories for analysis
        self.categories = {
            'Good': (0, 50),
            'Moderate': (51, 100),
            'Unhealthy for Sensitive Groups': (101, 150),
            'Unhealthy': (151, 200),
            'Very Unhealthy': (201, 300),
            'Hazardous': (301, 500)
        }
    
    def analyze_aqi_trends(self, df: pd.DataFrame, 
                          aqi_column: str = 'Calculated_AQI',
                          date_column: str = 'Timestamp') -> Dict[str, any]:
        """
        Analyze AQI trends over time
        
        Args:
            df: DataFrame with AQI data
            aqi_column: Name of AQI column
            date_column: Name of date column
            
        Returns:
            Dictionary with trend analysis results
        """
        if aqi_column not in df.columns:
            self.logger.error(f"AQI column {aqi_column} not found")
            return {}
        
        # Ensure date column is datetime
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
        
        # Calculate basic statistics
        aqi_stats = self.calculator.get_aqi_statistics(df, aqi_column)
        
        # Calculate trends
        if len(df) > 1:
            # Overall trend
            if date_column in df.columns:
                df_sorted = df.sort_values(date_column)
                x = np.arange(len(df_sorted))
                y = df_sorted[aqi_column].values
                
                # Linear regression for trend
                slope, intercept = np.polyfit(x, y, 1)
                trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                trend_strength = abs(slope)
            else:
                trend_direction = "unknown"
                trend_strength = 0.0
        else:
            trend_direction = "insufficient_data"
            trend_strength = 0.0
        
        # Category distribution over time
        if 'AQI_Category' in df.columns:
            category_trends = df.groupby('AQI_Category').size().to_dict()
        else:
            category_trends = {}
        
        return {
            'statistics': aqi_stats,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'category_distribution': category_trends,
            'data_points': len(df),
            'date_range': {
                'start': df[date_column].min().strftime('%Y-%m-%d') if date_column in df.columns else None,
                'end': df[date_column].max().strftime('%Y-%m-%d') if date_column in df.columns else None
            }
        }
    
    def identify_pollution_episodes(self, df: pd.DataFrame, 
                                 aqi_column: str = 'Calculated_AQI',
                                 threshold: int = 150) -> List[Dict]:
        """
        Identify pollution episodes (periods with high AQI)
        
        Args:
            df: DataFrame with AQI data
            aqi_column: Name of AQI column
            threshold: AQI threshold for episode detection
            
        Returns:
            List of pollution episodes
        """
        if aqi_column not in df.columns:
            self.logger.error(f"AQI column {aqi_column} not found")
            return []
        
        # Find periods where AQI exceeds threshold
        high_aqi_periods = df[df[aqi_column] >= threshold].copy()
        
        if len(high_aqi_periods) == 0:
            return []
        
        # Ensure date column is datetime
        if 'Timestamp' in high_aqi_periods.columns:
            high_aqi_periods['Timestamp'] = pd.to_datetime(high_aqi_periods['Timestamp'])
            high_aqi_periods = high_aqi_periods.sort_values('Timestamp')
        
        # Group consecutive high AQI days
        episodes = []
        current_episode = None
        
        for _, row in high_aqi_periods.iterrows():
            if current_episode is None:
                current_episode = {
                    'start_date': row['Timestamp'],
                    'end_date': row['Timestamp'],
                    'max_aqi': row[aqi_column],
                    'avg_aqi': row[aqi_column],
                    'days': 1,
                    'category': row.get('AQI_Category', 'Unknown')
                }
            else:
                # Check if consecutive day
                date_diff = (row['Timestamp'] - current_episode['end_date']).days
                if date_diff <= 1:  # Consecutive or same day
                    current_episode['end_date'] = row['Timestamp']
                    current_episode['max_aqi'] = max(current_episode['max_aqi'], row[aqi_column])
                    current_episode['days'] += 1
                else:
                    # End current episode and start new one
                    episodes.append(current_episode)
                    current_episode = {
                        'start_date': row['Timestamp'],
                        'end_date': row['Timestamp'],
                        'max_aqi': row[aqi_column],
                        'avg_aqi': row[aqi_column],
                        'days': 1,
                        'category': row.get('AQI_Category', 'Unknown')
                    }
        
        # Add the last episode
        if current_episode is not None:
            episodes.append(current_episode)
        
        # Calculate average AQI for each episode
        for episode in episodes:
            episode_data = df[(df['Timestamp'] >= episode['start_date']) & 
                            (df['Timestamp'] <= episode['end_date'])]
            if len(episode_data) > 0:
                episode['avg_aqi'] = episode_data[aqi_column].mean()
        
        return episodes
    
    def get_pollutant_contributions(self, df: pd.DataFrame, 
                                  pollutant_columns: List[str] = None) -> Dict[str, any]:
        """
        Analyze pollutant contributions to AQI
        
        Args:
            df: DataFrame with pollutant data
            pollutant_columns: List of pollutant columns to analyze
            
        Returns:
            Dictionary with pollutant contribution analysis
        """
        if pollutant_columns is None:
            pollutant_columns = ['PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'O3', 'NH3', 'NO', 'NOx', 'Benzene', 'Toluene', 'Xylene']
        
        # Filter available columns
        available_columns = [col for col in pollutant_columns if col in df.columns]
        
        if not available_columns:
            self.logger.warning("No pollutant columns found")
            return {}
        
        # Calculate sub-indices for each pollutant
        sub_indices = {}
        dominant_pollutants = []
        
        for _, row in df.iterrows():
            concentrations = {}
            for col in available_columns:
                if not pd.isna(row[col]):
                    concentrations[col] = row[col]
            
            if concentrations:
                dominant_pollutant, sub_index = self.calculator.get_dominant_pollutant(concentrations)
                dominant_pollutants.append(dominant_pollutant)
                
                # Calculate sub-indices for all pollutants
                for pollutant, conc in concentrations.items():
                    if pollutant not in sub_indices:
                        sub_indices[pollutant] = []
                    try:
                        sub_index = self.calculator.sub_index_functions[pollutant](conc)
                        sub_indices[pollutant].append(sub_index)
                    except:
                        sub_indices[pollutant].append(0)
        
        # Calculate average sub-indices
        avg_sub_indices = {}
        for pollutant, indices in sub_indices.items():
            if indices:
                avg_sub_indices[pollutant] = np.mean(indices)
        
        # Calculate dominant pollutant frequency
        dominant_frequency = pd.Series(dominant_pollutants).value_counts().to_dict()
        
        return {
            'average_sub_indices': avg_sub_indices,
            'dominant_pollutant_frequency': dominant_frequency,
            'most_dominant_pollutant': max(dominant_frequency, key=dominant_frequency.get) if dominant_frequency else None,
            'analyzed_pollutants': available_columns
        }
    
    def generate_aqi_report(self, df: pd.DataFrame, 
                           title: str = "AQI Analysis Report") -> Dict[str, any]:
        """
        Generate comprehensive AQI analysis report
        
        Args:
            df: DataFrame with AQI data
            title: Report title
            
        Returns:
            Dictionary with complete AQI analysis
        """
        # Calculate AQI if not already present
        if 'Calculated_AQI' not in df.columns:
            df = self.calculator.calculate_aqi_for_dataframe(df)
        
        # Trend analysis
        trend_analysis = self.analyze_aqi_trends(df)
        
        # Pollution episodes
        episodes = self.identify_pollution_episodes(df)
        
        # Pollutant contributions
        contributions = self.get_pollutant_contributions(df)
        
        # Health impact assessment
        health_impact = self.assess_health_impact(df)
        
        # Recommendations
        recommendations = self.generate_recommendations(trend_analysis, episodes, contributions)
        
        return {
            'title': title,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'standard': self.standard,
            'data_summary': {
                'total_records': len(df),
                'date_range': trend_analysis.get('date_range', {}),
                'categories': trend_analysis.get('category_distribution', {})
            },
            'trend_analysis': trend_analysis,
            'pollution_episodes': episodes,
            'pollutant_contributions': contributions,
            'health_impact': health_impact,
            'recommendations': recommendations
        }
    
    def assess_health_impact(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Assess health impact based on AQI categories
        
        Args:
            df: DataFrame with AQI data
            
        Returns:
            Dictionary with health impact assessment
        """
        if 'AQI_Category' not in df.columns:
            return {}
        
        # Count days in each category
        category_counts = df['AQI_Category'].value_counts().to_dict()
        total_days = len(df)
        
        # Calculate health risk metrics
        unhealthy_days = category_counts.get('Unhealthy', 0) + \
                        category_counts.get('Very Unhealthy', 0) + \
                        category_counts.get('Hazardous', 0)
        
        sensitive_group_days = category_counts.get('Unhealthy for Sensitive Groups', 0)
        
        health_risk_score = (unhealthy_days * 3 + sensitive_group_days * 2) / total_days if total_days > 0 else 0
        
        # Determine overall health risk level
        if health_risk_score < 0.5:
            risk_level = "Low"
        elif health_risk_score < 1.0:
            risk_level = "Moderate"
        elif health_risk_score < 2.0:
            risk_level = "High"
        else:
            risk_level = "Very High"
        
        return {
            'category_distribution': category_counts,
            'unhealthy_days': unhealthy_days,
            'sensitive_group_days': sensitive_group_days,
            'health_risk_score': round(health_risk_score, 2),
            'risk_level': risk_level,
            'total_analyzed_days': total_days
        }
    
    def generate_recommendations(self, trend_analysis: Dict, 
                               episodes: List[Dict], 
                               contributions: Dict) -> List[str]:
        """
        Generate recommendations based on AQI analysis
        
        Args:
            trend_analysis: Trend analysis results
            episodes: Pollution episodes
            contributions: Pollutant contribution analysis
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Trend-based recommendations
        trend_direction = trend_analysis.get('trend_direction', 'unknown')
        if trend_direction == 'increasing':
            recommendations.append("Air quality is deteriorating - implement stricter emission controls")
        elif trend_direction == 'decreasing':
            recommendations.append("Air quality is improving - continue current measures")
        
        # Episode-based recommendations
        if episodes:
            recommendations.append(f"Identified {len(episodes)} high pollution episodes - investigate sources")
            max_aqi = max([ep['max_aqi'] for ep in episodes])
            if max_aqi > 200:
                recommendations.append("Severe pollution episodes detected - implement emergency response plans")
        
        # Pollutant-based recommendations
        most_dominant = contributions.get('most_dominant_pollutant')
        if most_dominant:
            if most_dominant in ['PM2.5', 'PM10']:
                recommendations.append("Particulate matter is the primary concern - focus on dust control and vehicle emissions")
            elif most_dominant in ['NO2', 'NO', 'NOx']:
                recommendations.append("Nitrogen oxides are dominant - target vehicle and industrial emissions")
            elif most_dominant == 'CO':
                recommendations.append("Carbon monoxide is high - address incomplete combustion sources")
            elif most_dominant == 'SO2':
                recommendations.append("Sulfur dioxide is elevated - control industrial sulfur emissions")
            elif most_dominant == 'O3':
                recommendations.append("Ozone is the primary concern - control precursor emissions (NOx, VOCs)")
        
        # General recommendations
        recommendations.append("Continue regular air quality monitoring")
        recommendations.append("Increase public awareness during high pollution periods")
        
        return recommendations
    
    def create_aqi_dashboard_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Create data for AQI dashboard visualization
        
        Args:
            df: DataFrame with AQI data
            
        Returns:
            Dictionary with dashboard data
        """
        # Calculate AQI if not present
        if 'Calculated_AQI' not in df.columns:
            df = self.calculator.calculate_aqi_for_dataframe(df)
        
        # Time series data
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            time_series = df[['Timestamp', 'Calculated_AQI', 'AQI_Category']].to_dict('records')
        else:
            time_series = []
        
        # Category distribution
        category_dist = df['AQI_Category'].value_counts().to_dict()
        
        # Monthly averages
        if 'Timestamp' in df.columns:
            df['Month'] = df['Timestamp'].dt.month
            monthly_avg = df.groupby('Month')['Calculated_AQI'].mean().to_dict()
        else:
            monthly_avg = {}
        
        # Pollutant contributions
        contributions = self.get_pollutant_contributions(df)
        
        return {
            'time_series': time_series,
            'category_distribution': category_dist,
            'monthly_averages': monthly_avg,
            'pollutant_contributions': contributions,
            'statistics': self.calculator.get_aqi_statistics(df),
            'episodes': self.identify_pollution_episodes(df)
        }

# Factory function for creating AQI analyzer
def create_aqi_analyzer(standard: str = 'US_EPA') -> AQIAnalyzer:
    """Create AQI analyzer instance"""
    return AQIAnalyzer(standard)
