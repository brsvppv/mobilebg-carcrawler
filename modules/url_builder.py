"""
URL Builder Module for AutoGetCars Crawler
Builds mobile.bg search URLs from environment variables
"""

import os
import logging


def require_env(var, logger=None):
    """
    Get required environment variable with validation.
    
    Args:
        var (str): Environment variable name
        logger (logging.Logger, optional): Logger instance
        
    Returns:
        str: Environment variable value
        
    Raises:
        ValueError: If environment variable is missing
    """
    if logger is None:
        logger = logging.getLogger(__name__)
        
    val = os.getenv(var)
    if not val:
        logger.error(f"Missing required .env variable: {var}")
        raise ValueError(f"Missing required .env variable: {var}")
    return val


def build_mobilebg_search_url(logger=None):
    """
    Build mobile.bg search URL from environment variables.
    
    Args:
        logger (logging.Logger, optional): Logger instance
        
    Returns:
        str: Complete search URL
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    # Get required environment variables
    base_url = require_env('BASE_URL', logger)
    general_type = require_env('GENERAL_TYPE', logger)
    brand = require_env('BRAND', logger)
    model = require_env('MODEL', logger)
    vehicle_type = require_env('VEHICLE_TYPE', logger)
    min_price = require_env('MIN_PRICE', logger)
    max_price = require_env('MAX_PRICE', logger)
    min_engine_power = require_env('MIN_ENGINE_POWER', logger)
    max_engine_power = require_env('MAX_ENGINE_POWER', logger)
    fuel_type = require_env('FUEL_TYPE', logger)

    # Log search criteria
    logger.info("🔍 SEARCH CRITERIA:")
    logger.info(f"📱 Vehicle: {brand.title()} {model.title()} ({vehicle_type})")
    logger.info(f"⛽ Fuel Type: {fuel_type}")
    logger.info(f"💰 Price Range: {min_price} - {max_price} BGN")
    logger.info(f"🔧 Engine Power: {min_engine_power} - {max_engine_power} HP")

    # Build URL
    url = (
        f"{base_url}/{general_type}/{brand}/{model}/{vehicle_type}/{fuel_type}?"
        f"price={min_price}&price1={max_price}&engine_power={min_engine_power}&engine_power1={max_engine_power}"
    )
    
    return url