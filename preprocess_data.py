"""
Weather Data Preprocessing for Machine Learning
This script preprocesses weather data for predicting:
- Rainfall
- Windspeed
- Dust concentration
- Temperature
- And other weather variables
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class WeatherDataPreprocessor:
    def __init__(self, csv_path):
        """
        Initialize the preprocessor with the data path
        """
        self.df = pd.read_csv(csv_path)
        self.scaler_standard = StandardScaler()
        self.scaler_minmax = MinMaxScaler()
        
    def initial_inspection(self):
        """
        Inspect the data and print summary statistics
        """
        print("="*80)
        print("INITIAL DATA INSPECTION")
        print("="*80)
        print(f"\nDataset Shape: {self.df.shape}")
        print(f"\nColumns: {self.df.columns.tolist()}")
        print(f"\nData Types:\n{self.df.dtypes}")
        print(f"\nMissing Values:\n{self.df.isnull().sum()}")
        print(f"\nMissing Values (%):\n{(self.df.isnull().sum() / len(self.df) * 100).round(2)}")
        print(f"\nBasic Statistics:\n{self.df.describe()}")
        print("\n")
        
    def parse_dates(self):
        """
        Parse date column and extract temporal features
        """
        print("Parsing dates and extracting temporal features...")
        
        # Convert DATE to datetime
        self.df['DATE'] = pd.to_datetime(self.df['DATE'], format='%m/%d/%Y', errors='coerce')
        
        # Extract temporal features
        self.df['YEAR'] = self.df['DATE'].dt.year
        self.df['MONTH'] = self.df['DATE'].dt.month
        self.df['DAY'] = self.df['DATE'].dt.day
        self.df['DAY_OF_YEAR'] = self.df['DATE'].dt.dayofyear
        self.df['WEEK_OF_YEAR'] = self.df['DATE'].dt.isocalendar().week
        self.df['QUARTER'] = self.df['DATE'].dt.quarter
        
        # Cyclical encoding for temporal features (important for ML models)
        # Month cyclical encoding
        self.df['MONTH_SIN'] = np.sin(2 * np.pi * self.df['MONTH'] / 12)
        self.df['MONTH_COS'] = np.cos(2 * np.pi * self.df['MONTH'] / 12)
        
        # Day of year cyclical encoding
        self.df['DAY_OF_YEAR_SIN'] = np.sin(2 * np.pi * self.df['DAY_OF_YEAR'] / 365)
        self.df['DAY_OF_YEAR_COS'] = np.cos(2 * np.pi * self.df['DAY_OF_YEAR'] / 365)
        
        # Season feature
        self.df['SEASON'] = self.df['MONTH'].apply(self._get_season)
        
        print("✓ Date parsing completed")
        
    def _get_season(self, month):
        """
        Get season from month (Northern Hemisphere)
        """
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    def handle_missing_values(self):
        """
        Handle missing values intelligently
        """
        print("\nHandling missing values...")
        
        # For temperature variables, use interpolation (more accurate for continuous data)
        temp_columns = ['TAVG', 'TMAX', 'TMIN']
        
        for col in temp_columns:
            if col in self.df.columns:
                # Linear interpolation
                self.df[col] = self.df[col].interpolate(method='linear', limit_direction='both')
                # Fill any remaining NaNs with forward fill, then backward fill
                self.df[col] = self.df[col].fillna(method='ffill').fillna(method='bfill')
        
        # For precipitation, missing values likely mean no rain (0)
        if 'PRCP' in self.df.columns:
            self.df['PRCP'] = self.df['PRCP'].fillna(0)
        
        print(f"✓ Missing values handled")
        print(f"  Remaining missing values: {self.df.isnull().sum().sum()}")
        
    def create_derived_features(self):
        """
        Create derived features that are useful for weather prediction
        """
        print("\nCreating derived features...")
        
        # Temperature-related features
        if all(col in self.df.columns for col in ['TMAX', 'TMIN']):
            # Daily temperature range
            self.df['TEMP_RANGE'] = self.df['TMAX'] - self.df['TMIN']
            
            # Temperature average (if TAVG is missing, calculate it)
            if 'TAVG' in self.df.columns:
                self.df['TAVG'] = self.df['TAVG'].fillna((self.df['TMAX'] + self.df['TMIN']) / 2)
            else:
                self.df['TAVG'] = (self.df['TMAX'] + self.df['TMIN']) / 2
        
        # Precipitation features
        if 'PRCP' in self.df.columns:
            # Binary: Did it rain?
            self.df['IS_RAINY'] = (self.df['PRCP'] > 0).astype(int)
            
            # Precipitation intensity categories
            self.df['PRCP_INTENSITY'] = pd.cut(
                self.df['PRCP'], 
                bins=[-0.01, 0, 0.1, 0.3, 1.0, float('inf')],
                labels=['None', 'Light', 'Moderate', 'Heavy', 'Very Heavy']
            )
        
        # Rolling/Moving averages (capture trends)
        window_sizes = [3, 7, 14, 30]
        
        for window in window_sizes:
            if 'TAVG' in self.df.columns:
                self.df[f'TAVG_MA_{window}D'] = self.df['TAVG'].rolling(window=window, min_periods=1).mean()
                self.df[f'TAVG_STD_{window}D'] = self.df['TAVG'].rolling(window=window, min_periods=1).std()
            
            if 'PRCP' in self.df.columns:
                self.df[f'PRCP_SUM_{window}D'] = self.df['PRCP'].rolling(window=window, min_periods=1).sum()
                self.df[f'PRCP_MA_{window}D'] = self.df['PRCP'].rolling(window=window, min_periods=1).mean()
        
        # Lag features (previous days' values)
        lag_days = [1, 2, 3, 7, 14]
        
        for lag in lag_days:
            if 'TAVG' in self.df.columns:
                self.df[f'TAVG_LAG_{lag}D'] = self.df['TAVG'].shift(lag)
            
            if 'PRCP' in self.df.columns:
                self.df[f'PRCP_LAG_{lag}D'] = self.df['PRCP'].shift(lag)
        
        # Fill NaN values created by lag and rolling features
        self.df = self.df.fillna(method='bfill')
        
        print(f"✓ Derived features created")
        print(f"  Total features now: {len(self.df.columns)}")
        
    def detect_and_handle_outliers(self):
        """
        Detect and handle outliers using IQR method
        """
        print("\nDetecting and handling outliers...")
        
        numerical_columns = self.df.select_dtypes(include=[np.number]).columns
        outlier_counts = {}
        
        for col in numerical_columns:
            if col not in ['YEAR', 'MONTH', 'DAY', 'DAY_OF_YEAR', 'WEEK_OF_YEAR', 'QUARTER', 'IS_RAINY']:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 3 * IQR  # Using 3*IQR for more lenient outlier detection
                upper_bound = Q3 + 3 * IQR
                
                outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
                
                if outliers > 0:
                    outlier_counts[col] = outliers
                    # Cap outliers instead of removing (to preserve data)
                    self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
        
        print(f"✓ Outliers handled (capped)")
        if outlier_counts:
            for col, count in outlier_counts.items():
                print(f"  {col}: {count} outliers capped")
        else:
            print("  No significant outliers detected")
    
    def create_target_variables(self):
        """
        Create target variables for different prediction tasks
        """
        print("\nCreating target variables for prediction tasks...")
        
        # Rainfall prediction (next day)
        if 'PRCP' in self.df.columns:
            self.df['TARGET_RAINFALL_NEXT_DAY'] = self.df['PRCP'].shift(-1)
            self.df['TARGET_WILL_RAIN_NEXT_DAY'] = (self.df['TARGET_RAINFALL_NEXT_DAY'] > 0).astype(int)
        
        # Temperature prediction (next day)
        if 'TAVG' in self.df.columns:
            self.df['TARGET_TEMP_NEXT_DAY'] = self.df['TAVG'].shift(-1)
        
        if 'TMAX' in self.df.columns:
            self.df['TARGET_TMAX_NEXT_DAY'] = self.df['TMAX'].shift(-1)
        
        if 'TMIN' in self.df.columns:
            self.df['TARGET_TMIN_NEXT_DAY'] = self.df['TMIN'].shift(-1)
        
        # Multi-day ahead predictions (3 days, 7 days)
        for days_ahead in [3, 7]:
            if 'PRCP' in self.df.columns:
                self.df[f'TARGET_RAINFALL_{days_ahead}D'] = self.df['PRCP'].shift(-days_ahead)
            if 'TAVG' in self.df.columns:
                self.df[f'TARGET_TEMP_{days_ahead}D'] = self.df['TAVG'].shift(-days_ahead)
        
        print("✓ Target variables created")
        
    def encode_categorical_features(self):
        """
        Encode categorical features
        """
        print("\nEncoding categorical features...")
        
        # One-hot encode season
        if 'SEASON' in self.df.columns:
            season_dummies = pd.get_dummies(self.df['SEASON'], prefix='SEASON')
            self.df = pd.concat([self.df, season_dummies], axis=1)
        
        # One-hot encode precipitation intensity
        if 'PRCP_INTENSITY' in self.df.columns:
            intensity_dummies = pd.get_dummies(self.df['PRCP_INTENSITY'], prefix='PRCP_INTENSITY')
            self.df = pd.concat([self.df, intensity_dummies], axis=1)
        
        print("✓ Categorical features encoded")
        
    def normalize_features(self):
        """
        Create normalized versions of numerical features
        """
        print("\nCreating normalized feature sets...")
        
        # Columns to normalize
        numerical_features = [
            'TAVG', 'TMAX', 'TMIN', 'PRCP', 'TEMP_RANGE'
        ]
        
        # Add rolling averages to normalization
        rolling_cols = [col for col in self.df.columns if 'MA' in col or 'STD' in col or 'LAG' in col or 'SUM' in col]
        numerical_features.extend(rolling_cols)
        
        # Filter only existing columns
        numerical_features = [col for col in numerical_features if col in self.df.columns]
        
        # Create standardized features (mean=0, std=1)
        standardized_features = self.df[numerical_features].copy()
        standardized_features = pd.DataFrame(
            self.scaler_standard.fit_transform(standardized_features),
            columns=[f'{col}_STANDARDIZED' for col in numerical_features],
            index=self.df.index
        )
        
        # Create normalized features (0-1 range)
        normalized_features = self.df[numerical_features].copy()
        normalized_features = pd.DataFrame(
            self.scaler_minmax.fit_transform(normalized_features),
            columns=[f'{col}_NORMALIZED' for col in numerical_features],
            index=self.df.index
        )
        
        # Add to main dataframe
        self.df = pd.concat([self.df, standardized_features, normalized_features], axis=1)
        
        print("✓ Normalized features created")
        print(f"  Added {len(standardized_features.columns)} standardized features")
        print(f"  Added {len(normalized_features.columns)} normalized features")
    
    def create_feature_sets(self):
        """
        Create different feature sets for different ML tasks
        """
        print("\nCreating feature sets for different tasks...")
        
        # Remove rows with NaN in target variables (last few rows)
        self.df = self.df.dropna(subset=[col for col in self.df.columns if col.startswith('TARGET_')])
        
        # Define feature groups
        temporal_features = [col for col in self.df.columns if any(x in col for x in ['YEAR', 'MONTH', 'DAY', 'WEEK', 'QUARTER', 'SEASON', 'SIN', 'COS'])]
        
        basic_weather_features = ['TAVG', 'TMAX', 'TMIN', 'PRCP', 'TEMP_RANGE', 'IS_RAINY']
        basic_weather_features = [col for col in basic_weather_features if col in self.df.columns]
        
        rolling_features = [col for col in self.df.columns if any(x in col for x in ['MA_', 'STD_', 'SUM_'])]
        
        lag_features = [col for col in self.df.columns if 'LAG_' in col]
        
        normalized_features = [col for col in self.df.columns if 'NORMALIZED' in col or 'STANDARDIZED' in col]
        
        # Create metadata for feature sets
        self.feature_sets = {
            'temporal': temporal_features,
            'basic_weather': basic_weather_features,
            'rolling': rolling_features,
            'lag': lag_features,
            'normalized': normalized_features,
            'all_features': temporal_features + basic_weather_features + rolling_features + lag_features
        }
        
        print("✓ Feature sets created")
        for name, features in self.feature_sets.items():
            print(f"  {name}: {len(features)} features")
    
    def save_processed_data(self):
        """
        Save processed datasets - ALL IN ONE FILE
        """
        print("\n" + "="*80)
        print("SAVING PROCESSED DATA")
        print("="*80)
        
        # Save complete processed dataset - SINGLE FILE
        output_file = "data/weather_processed_ml_ready.csv"
        self.df.to_csv(output_file, index=False)
        print(f"✓ Complete dataset saved: {output_file}")
        print(f"  Shape: {self.df.shape}")
        print(f"  All features and targets included in one file!")
        
        # Save data dictionary and feature information as text file
        self._save_data_dictionary()
        
    def _save_data_dictionary(self):
        """
        Save a data dictionary explaining all features
        """
        dict_file = "data/data_dictionary.txt"
        
        with open(dict_file, 'w') as f:
            f.write("WEATHER DATA DICTIONARY - ML READY\n")
            f.write("="*80 + "\n\n")
            
            f.write("OUTPUT FILE: weather_processed_ml_ready.csv\n")
            f.write(f"Total Features: {len(self.df.columns)}\n")
            f.write(f"Total Samples: {len(self.df)}\n\n")
            
            f.write("ORIGINAL FEATURES:\n")
            f.write("-"*80 + "\n")
            f.write("STATION: Weather station ID\n")
            f.write("NAME: Weather station name\n")
            f.write("DATE: Date of observation\n")
            f.write("PRCP: Precipitation (inches)\n")
            f.write("TAVG: Average temperature (°F)\n")
            f.write("TMAX: Maximum temperature (°F)\n")
            f.write("TMIN: Minimum temperature (°F)\n\n")
            
            f.write("TEMPORAL FEATURES:\n")
            f.write("-"*80 + "\n")
            f.write("YEAR, MONTH, DAY: Date components\n")
            f.write("DAY_OF_YEAR: Day number in year (1-365)\n")
            f.write("WEEK_OF_YEAR: Week number in year\n")
            f.write("QUARTER: Quarter of the year (1-4)\n")
            f.write("MONTH_SIN, MONTH_COS: Cyclical encoding of month\n")
            f.write("DAY_OF_YEAR_SIN, DAY_OF_YEAR_COS: Cyclical encoding of day of year\n")
            f.write("SEASON: Season (Winter, Spring, Summer, Fall)\n\n")
            
            f.write("DERIVED FEATURES:\n")
            f.write("-"*80 + "\n")
            f.write("TEMP_RANGE: Daily temperature range (TMAX - TMIN)\n")
            f.write("IS_RAINY: Binary indicator (1 if PRCP > 0)\n")
            f.write("PRCP_INTENSITY: Categorical precipitation intensity\n\n")
            
            f.write("ROLLING/MOVING AVERAGE FEATURES:\n")
            f.write("-"*80 + "\n")
            f.write("*_MA_XD: Moving average over X days\n")
            f.write("*_STD_XD: Moving standard deviation over X days\n")
            f.write("PRCP_SUM_XD: Sum of precipitation over X days\n")
            f.write("Windows: 3, 7, 14, 30 days\n\n")
            
            f.write("LAG FEATURES:\n")
            f.write("-"*80 + "\n")
            f.write("*_LAG_XD: Value from X days ago\n")
            f.write("Lags: 1, 2, 3, 7, 14 days\n\n")
            
            f.write("NORMALIZED FEATURES:\n")
            f.write("-"*80 + "\n")
            f.write("*_STANDARDIZED: Z-score normalization (mean=0, std=1)\n")
            f.write("*_NORMALIZED: Min-Max normalization (0-1 range)\n\n")
            
            f.write("TARGET VARIABLES:\n")
            f.write("-"*80 + "\n")
            f.write("TARGET_RAINFALL_NEXT_DAY: Precipitation amount next day\n")
            f.write("TARGET_WILL_RAIN_NEXT_DAY: Binary (1 if rain next day)\n")
            f.write("TARGET_TEMP_NEXT_DAY: Average temperature next day\n")
            f.write("TARGET_TMAX_NEXT_DAY: Maximum temperature next day\n")
            f.write("TARGET_TMIN_NEXT_DAY: Minimum temperature next day\n")
            f.write("TARGET_*_3D, TARGET_*_7D: Predictions 3 and 7 days ahead\n\n")
            
            f.write("FEATURE SETS (for easy selection):\n")
            f.write("-"*80 + "\n\n")
            
            for name, features in self.feature_sets.items():
                f.write(f"{name.upper()} ({len(features)} features):\n")
                for feature in features[:10]:  # Show first 10
                    f.write(f"  - {feature}\n")
                if len(features) > 10:
                    f.write(f"  ... and {len(features) - 10} more\n")
                f.write("\n")
            
            f.write("USAGE RECOMMENDATIONS:\n")
            f.write("-"*80 + "\n")
            f.write("1. Use STANDARDIZED features for models sensitive to scale (SVM, Neural Networks)\n")
            f.write("2. Use NORMALIZED features for models requiring 0-1 range\n")
            f.write("3. Include temporal features for capturing seasonality\n")
            f.write("4. Use rolling features for capturing trends\n")
            f.write("5. Use lag features for time series models (LSTM, ARIMA)\n")
            f.write("6. Remove highly correlated features for linear models\n")
            f.write("7. Consider feature selection for high-dimensional datasets\n\n")
            
            f.write("HOW TO USE THE DATA:\n")
            f.write("-"*80 + "\n")
            f.write("1. Load: df = pd.read_csv('data/weather_processed_ml_ready.csv')\n")
            f.write("2. Select features based on your task (see FEATURE SETS above)\n")
            f.write("3. Select appropriate target variable (TARGET_*)\n")
            f.write("4. Split into train/validation/test sets\n")
            f.write("5. Train your ML model\n")
            f.write("6. Evaluate and tune\n")
        
        print("✓ Data dictionary saved: {dict_file}")
    
    def save_basic_data(self):
        """
        Save only basic cleaned weather data
        """
        print("\n" + "="*80)
        print("SAVING CLEANED DATA - BASIC FEATURES ONLY")
        print("="*80)
        
        # Keep only the essential columns
        basic_columns = ['STATION', 'NAME', 'DATE', 'YEAR', 'MONTH', 'DAY', 
                        'PRCP', 'TAVG', 'TMAX', 'TMIN']
        
        # Select only existing columns
        basic_columns = [col for col in basic_columns if col in self.df.columns]
        
        basic_df = self.df[basic_columns].copy()
        
        # Save to single file
        output_file = "data/weather_cleaned.csv"
        basic_df.to_csv(output_file, index=False)
        
        print(f"✓ Cleaned dataset saved: {output_file}")
        print(f"  Shape: {basic_df.shape}")
        print(f"  Columns: {basic_df.columns.tolist()}")
        print("\n  Features included:")
        print("    • STATION - Weather station ID")
        print("    • NAME - Station name")
        print("    • DATE - Date of observation")
        print("    • YEAR, MONTH, DAY - Date components")
        print("    • PRCP - Precipitation (inches)")
        print("    • TAVG - Average temperature (°F)")
        print("    • TMAX - Maximum temperature (°F)")
        print("    • TMIN - Minimum temperature (°F)")
    
    def generate_basic_summary(self):
        """
        Generate summary for basic preprocessing
        """
        print("\n" + "="*80)
        print("PREPROCESSING COMPLETED!")
        print("="*80)
        
        print("\nData Quality:")
        print(f"  ✓ Missing values handled")
        print(f"  ✓ Dates parsed and cleaned")
        print(f"  ✓ Ready for machine learning")
        
        print("\n🎯 Output File:")
        print("  ✓ data/weather_cleaned.csv")
        
        print("\nNext Steps:")
        print("1. Load: df = pd.read_csv('data/weather_cleaned.csv')")
        print("2. Create your own features as needed")
        print("3. Split into train/test sets")
        print("4. Train your ML models")
        print("="*80 + "\n")

    
    def generate_summary_report(self):
        """
        Generate a summary report of the preprocessing
        """
        print("\n" + "="*80)
        print("PREPROCESSING SUMMARY REPORT")
        print("="*80)
        
        print(f"\nFinal Dataset Shape: {self.df.shape}")
        print(f"Total Features: {len(self.df.columns)}")
        print(f"\nFeature Breakdown:")
        print(f"  - Temporal features: {len(self.feature_sets['temporal'])}")
        print(f"  - Basic weather features: {len(self.feature_sets['basic_weather'])}")
        print(f"  - Rolling features: {len(self.feature_sets['rolling'])}")
        print(f"  - Lag features: {len(self.feature_sets['lag'])}")
        print(f"  - Normalized features: {len(self.feature_sets['normalized'])}")
        
        print(f"\nData Quality:")
        print(f"  - Missing values: {self.df.isnull().sum().sum()}")
        print(f"  - Duplicate rows: {self.df.duplicated().sum()}")
        
        print(f"\nTarget Variables:")
        target_cols = [col for col in self.df.columns if col.startswith('TARGET_')]
        for target in target_cols:
            print(f"  - {target}: {self.df[target].notna().sum()} samples")
        
        print("\n" + "="*80)
        print("PREPROCESSING COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nNext Steps:")
        print("1. Load the processed dataset from 'data/weather_processed_ml_ready.csv'")
        print("2. Read the data dictionary in 'data/data_dictionary.txt'")
        print("3. Split data into train/validation/test sets")
        print("4. Select appropriate features for your specific ML task")
        print("5. Train your models (Random Forest, XGBoost, LSTM, etc.)")
        print("6. Evaluate and tune hyperparameters")
        print("\n🎯 Single Output File Created:")
        print("  ✓ data/weather_processed_ml_ready.csv (ALL data in one file!)")
        print("  ✓ data/data_dictionary.txt (documentation)")
        print("="*80 + "\n")

    
    def run_full_preprocessing(self):
        """
        Run the complete preprocessing pipeline - BASIC FEATURES ONLY
        """
        print("\n" + "="*80)
        print("STARTING WEATHER DATA PREPROCESSING PIPELINE")
        print("Basic Weather Features Only - Simple & Clean")
        print("="*80 + "\n")
        
        self.initial_inspection()
        self.parse_dates()
        self.handle_missing_values()
        # Skip derived features, rolling averages, lags, normalization
        # self.create_derived_features()
        # self.detect_and_handle_outliers()
        # self.create_target_variables()
        # self.encode_categorical_features()
        # self.normalize_features()
        # self.create_feature_sets()
        self.save_basic_data()
        self.generate_basic_summary()


def main():
    """
    Main execution function
    """
    # Process Alexandria weather data
    print("Processing Alexandria Weather Data...")
    preprocessor = WeatherDataPreprocessor('data/weather_alex.csv')
    preprocessor.run_full_preprocessing()


if __name__ == "__main__":
    main()