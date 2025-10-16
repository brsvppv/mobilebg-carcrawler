#!/usr/bin/env python3
"""
AutoGetCars Crawler - Main Entry Point
Command-line interface for crawling car data from mobile.bg
"""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.config_manager import load_env_config, get_output_config
from modules.logger_config import setup_logging
from modules.url_builder import build_mobilebg_search_url
from modules.url_validator import validate_search_url
from modules.web_scraper import get_all_listing_links
from modules import excel_utils
from modules.extractors import extract_car_info_unified


def main():
    """Main crawler function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AutoGetCars Crawler - Extract car data from mobile.bg')
    parser.add_argument('--delay', type=float, default=0.5, 
                       help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--max-pages', type=int, default=100,
                       help='Maximum pages to crawl (default: 100)')
    parser.add_argument('--excel', type=str, default='docs/car-data.xlsx',
                       help='Excel output file path (default: docs/car-data.xlsx)')
    
    args = parser.parse_args()
    
    # Load configuration
    load_env_config()
    
    # Setup logging
    logger = setup_logging()
    
    # Log session start
    logger.info("=" * 80)
    logger.info("🚀 NEW CRAWLER SESSION STARTED")
    logger.info("=" * 80)
    
    # Log arguments
    logger.info(f"🎮 Crawler Arguments: delay={args.delay}s, max_pages={args.max_pages}, excel={args.excel}")
    
    try:
        # Build search URL
        search_url = build_mobilebg_search_url(logger)
        
        # Validate URL before proceeding
        if not validate_search_url(search_url, logger):
            logger.error("❌ Search URL validation failed. Please check your configuration.")
            raise ValueError("Invalid search URL - check brand, model, vehicle type, and fuel type")
        
        # Get all listing links
        links = get_all_listing_links(search_url, delay=args.delay, max_pages=args.max_pages, logger=logger)
        
        if not links:
            logger.error("❌ No car links found. Exiting.")
            return
        
        # Extract data from each car listing
        logger.info("🚗 STARTING DATA EXTRACTION:")
        logger.info(f"  📊 Total Links to Process: {len(links)} cars")
        logger.info(f"  ⏱️  Estimated Time: ~{len(links) * 0.3:.1f} seconds")
        
        cars_data = []
        start_time = time.time()
        batch_size = 10
        
        for i, link in enumerate(links, 1):
            try:
                # Progress logging
                if i % batch_size == 1 or i == len(links):
                    progress = (i / len(links)) * 100
                    logger.info(f"  [{i}/{len(links)}] ({progress:.1f}%) Processing batch...")
                
                # Extract individual car data with progress
                if i % batch_size != 1:  # Don't duplicate the first one
                    progress = (i / len(links)) * 100
                    link_id = link.split('/')[-1] if '/' in link else link[-50:]
                    logger.info(f"  [{i}/{len(links)}] ({progress:.1f}%) Extracting: {link_id}...")
                
                car_info = extract_car_info_unified(link)
                if car_info:
                    cars_data.append(car_info)
                
                # Add delay between extractions
                if args.delay > 0:
                    time.sleep(args.delay)
                    
            except KeyboardInterrupt:
                logger.warning("🛑 Crawling interrupted by user")
                break
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract data from {link}: {e}")
                continue
        
        # Log extraction results
        extraction_time = time.time() - start_time
        success_count = len(cars_data)
        fail_count = len(links) - success_count
        success_rate = (success_count / len(links)) * 100 if links else 0
        
        logger.info("📈 EXTRACTION COMPLETE!")
        logger.info(f"  ✅ Successful Extractions: {success_count} cars")
        logger.info(f"  ❌ Failed Extractions: {fail_count} cars")
        logger.info(f"  📊 Success Rate: {success_rate:.1f}%")
        logger.info(f"  ⏱️  Total Extraction Time: {extraction_time:.1f} seconds")
        logger.info(f"  ⚡ Average Time per Car: {extraction_time/len(links):.2f} seconds")
        
        if not cars_data:
            logger.error("❌ No car data extracted successfully.")
            return
        
        # Analyze price data
        prices = [car.get('price_numeric') for car in cars_data if car.get('price_numeric')]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            logger.info("💰 PRICE ANALYSIS:")
            logger.info(f"  📊 Cars with Valid Prices: {len(prices)}/{len(cars_data)}")
            logger.info(f"  💵 Average Price: {avg_price:,.0f} BGN")
            logger.info(f"  📉 Minimum Price: {min_price:,.0f} BGN")
            logger.info(f"  📈 Maximum Price: {max_price:,.0f} BGN")
        
        # Export to Excel
        output_config = get_output_config()
        excel_utils.export_to_excel(
            cars_data, 
            args.excel,
            sheet_name=output_config.get('sheet_name', 'CarsData')
        )
        
        logger.info("💾 EXCEL EXPORT COMPLETE!")
        logger.info(f"  📁 File: {args.excel}")
        
        # Determine sheet name based on search criteria
        import os
        brand = os.getenv('BRAND', 'Cars').title()
        model = os.getenv('MODEL', '').title()
        sheet_name = f"{brand}-{model}" if model else brand
        
        logger.info(f"  📋 Sheet: {sheet_name}")
        logger.info(f"  📊 Records Saved: {len(cars_data)} cars")
        
        logger.info("🎯 MISSION COMPLETE! 🚀")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.warning("🛑 Crawler interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()