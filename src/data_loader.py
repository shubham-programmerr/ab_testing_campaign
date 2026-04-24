"""
Data Loader Module for A/B Testing Campaign Analysis Project
Handles data loading, validation, and initial data exploration
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

class DataLoader:
    """Load and validate A/B testing data."""
    
    def __init__(self, data_dir: str = 'data/raw'):
        """Initialize data loader with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV file into pandas DataFrame."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        return df
    
    def validate_ab_data(self, df: pd.DataFrame) -> bool:
        """
        Validate A/B testing data structure.
        Required columns: user_id, variant (control/treatment), metric, timestamp
        """
        required_cols = {'user_id', 'variant', 'metric', 'timestamp'}
        missing = required_cols - set(df.columns)
        
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Check for valid variants
        valid_variants = {'control', 'treatment'}
        invalid = set(df['variant'].unique()) - valid_variants
        if invalid:
            raise ValueError(f"Invalid variant values: {invalid}")
        
        return True
    
    def check_data_quality(self, df: pd.DataFrame) -> dict:
        """Check data quality metrics."""
        quality_report = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'control_count': (df['variant'] == 'control').sum(),
            'treatment_count': (df['variant'] == 'treatment').sum()
        }
        return quality_report
    
    def split_by_variant(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into control and treatment groups."""
        control = df[df['variant'] == 'control'].copy()
        treatment = df[df['variant'] == 'treatment'].copy()
        return control, treatment
