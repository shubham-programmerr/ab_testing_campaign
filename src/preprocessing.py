"""
Data Preprocessing Module for A/B Testing Campaign Analysis Project
Handles data cleaning, transformation, and Sample Ratio Mismatch checks
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple

class DataPreprocessor:
    """Clean and prepare data for A/B testing analysis."""
    
    def __init__(self):
        """Initialize preprocessor."""
        self.processing_log = []
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records, keeping first occurrence."""
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            self.processing_log.append(f"Removed {duplicates} duplicate records")
            df = df.drop_duplicates(keep='first')
        return df
    
    def handle_missing_values(self, df: pd.DataFrame, method: str = 'drop') -> pd.DataFrame:
        """Handle missing values (drop or forward-fill)."""
        missing_count = df.isnull().sum().sum()
        
        if missing_count == 0:
            return df
        
        if method == 'drop':
            df = df.dropna()
            self.processing_log.append(f"Dropped {missing_count} rows with missing values")
        elif method == 'forward_fill':
            df = df.fillna(method='ffill')
            self.processing_log.append(f"Forward-filled {missing_count} missing values")
        
        return df
    
    def check_sample_ratio_mismatch(self, df: pd.DataFrame, alpha: float = 0.05) -> Dict:
        """
        Check for Sample Ratio Mismatch (SRM) between control and treatment.
        Uses chi-square test for goodness of fit.
        """
        from scipy.stats import chisquare
        
        counts = df['variant'].value_counts()
        control_n = counts.get('control', 0)
        treatment_n = counts.get('treatment', 0)
        
        total = control_n + treatment_n
        expected = total / 2  # Expected equal split
        
        # Chi-square test
        chi2, p_value = chisquare([control_n, treatment_n], f_exp=[expected, expected])
        
        srm_result = {
            'control_count': control_n,
            'treatment_count': treatment_n,
            'total_count': total,
            'chi_square_stat': chi2,
            'p_value': p_value,
            'has_srm': p_value < alpha,
            'message': 'Sample Ratio Mismatch detected!' if p_value < alpha else 'No SRM detected'
        }
        
        return srm_result
    
    def remove_outliers(self, df: pd.DataFrame, numeric_columns: list, 
                       method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """Remove outliers using IQR method."""
        if method == 'iqr':
            for col in numeric_columns:
                if col in df.columns and df[col].dtype in [np.float64, np.int64]:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    
                    outliers = len(df[(df[col] < lower_bound) | (df[col] > upper_bound)])
                    if outliers > 0:
                        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                        self.processing_log.append(f"Removed {outliers} outliers from {col}")
        
        return df
    
    def normalize_column(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        """Normalize a column to 0-1 range."""
        if col in df.columns:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df[col] = (df[col] - min_val) / (max_val - min_val)
        return df
    
    def prepare_for_analysis(self, df: pd.DataFrame, numeric_cols: list = None) -> pd.DataFrame:
        """Complete preprocessing pipeline."""
        df = self.remove_duplicates(df)
        df = self.handle_missing_values(df, method='drop')
        
        if numeric_cols:
            df = self.remove_outliers(df, numeric_cols)
        
        self.processing_log.append("Data preprocessing completed")
        return df
    
    def get_processing_log(self) -> list:
        """Return processing log."""
        return self.processing_log
