"""
URL Validation Module for AutoGetCars Crawler
Validates mobile.bg search URLs before crawling
"""

import requests
import logging


def validate_search_url(url, logger=None):
    """
    Validate that the search URL exists and returns valid content.
    
    Args:
        url (str): The URL to validate
        logger (logging.Logger, optional): Logger instance for output
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔍 Validating search URL...")
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 404:
            logger.error(f"❌ URL returns 404 - Invalid brand/model/vehicle type combination")
            logger.error(f"🔗 URL: {url}")
            logger.error("💡 Check that:")
            logger.error("   - Brand and model exist on mobile.bg")
            logger.error("   - Vehicle type is correct: van, kabrio, kombi, dzhip, sedan, hechbek, minivan")
            logger.error("   - Fuel type is correct: dizelov, benzinov, hibriden, elektricheski")
            return False
            
        elif response.status_code != 200:
            logger.error(f"❌ URL validation failed with status code: {response.status_code}")
            logger.error(f"🔗 URL: {url}")
            return False
            
        # Check if the page contains search results
        if "Няма намерени обяви" in response.text or "No ads found" in response.text:
            logger.warning(f"⚠️ No results found for this search configuration")
            logger.warning(f"🔗 URL: {url}")
            logger.warning("💡 Try adjusting price range or engine power limits")
            return False
            
        logger.info(f"✅ URL validation successful")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error during URL validation: {e}")
        logger.error(f"🔗 URL: {url}")
        return False