"""
Configuration Manager for AutoGetCars Crawler
Handles environment file loading and configuration management
"""

import os
import sys
import pathlib
from dotenv import load_dotenv


def load_env_config(env_file=None):
    """
    Load environment configuration from .env file.
    
    Args:
        env_file (str, optional): Path to specific .env file
        
    Returns:
        pathlib.Path: Path to the loaded .env file
    """
    # Determine which .env file to use
    if env_file:
        dotenv_path = pathlib.Path(env_file)
    else:
        custom_env_file = os.environ.get('ENV_FILE')
        if custom_env_file:
            dotenv_path = pathlib.Path(custom_env_file)
        else:
            dotenv_path = pathlib.Path(__file__).parent.parent / '.env'
    
    # Check if file exists
    if not dotenv_path.exists():
        print(f"[ERROR] Environment file not found at {dotenv_path}")
        sys.exit(1)
    
    # Load the environment file
    load_dotenv(dotenv_path=str(dotenv_path))
    print(f"📁 Loaded configuration from: {dotenv_path.name}")
    
    return dotenv_path


def get_output_config():
    """
    Get output configuration from environment variables.
    
    Returns:
        dict: Output configuration parameters
    """
    return {
        'table_name': os.getenv('TABLE_NAME', 'CarsData'),
        'excel_path': os.getenv('EXCEL_PATH', 'docs/car-data.xlsx'),
        'excel_dir': os.getenv('EXCEL_DIR', 'docs'),
        'excel_file': os.getenv('EXCEL_FILE', 'car-data.xlsx'),
        'sheet_name': os.getenv('SHEET_NAME', 'CarsData')
    }