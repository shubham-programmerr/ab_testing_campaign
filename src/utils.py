"""
Utility functions for A/B Testing Campaign Analysis Project
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def ensure_directory(directory: str) -> None:
    """Ensure directory exists, create if not."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_project_root() -> Path:
    """Get the root directory of the project."""
    return Path(__file__).parent.parent

def validate_data_columns(df, required_columns: list) -> bool:
    """Validate that dataframe contains required columns."""
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return True
