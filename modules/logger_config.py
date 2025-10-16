"""
Logging Module for AutoGetCars Crawler
Provides comprehensive logging setup for both console and file output
"""

import os
import logging


def setup_logging(log_file='crawler.log'):
    """
    Setup comprehensive logging for both console and file output.
    
    Args:
        log_file (str): Name of the log file (default: 'crawler.log')
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('autogetcars_crawler')
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler for detailed logs
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), log_file)
    file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger