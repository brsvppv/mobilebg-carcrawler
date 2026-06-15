import threading
import time
import os
import sys
import logging
from pathlib import Path
from django.utils import timezone
from .models import CrawlSession, CarListing, SearchPreset
from modules.url_builder import build_mobilebg_search_url
from modules.url_validator import validate_search_url
from modules.web_scraper import get_all_listing_links
from modules.extractors import extract_car_info_unified
from modules import excel_utils

# Dictionary to keep track of active threads
ACTIVE_CRAWLS = {}

class SessionLogHandler(logging.Handler):
    """Custom logging handler to append logs directly to a CrawlSession in the database."""
    def __init__(self, session_id):
        super().__init__()
        self.session_id = session_id

    def emit(self, record):
        try:
            log_entry = self.format(record)
            # Fetch fresh session and append logs
            session = CrawlSession.objects.get(id=self.session_id)
            session.logs = (session.logs or '') + log_entry + '\n'
            session.save(update_fields=['logs'])
        except Exception:
            pass # Avoid throwing exceptions during logging

def run_crawl_session(session_id, brand, model, vehicle_type, fuel_type, min_price, max_price, min_power, max_power, max_pages, delay):
    """Executes the crawl in a background thread."""
    # Setup temporary environment variables to mimic .env settings for standard modules
    os.environ['BRAND'] = brand
    os.environ['MODEL'] = model
    os.environ['VEHICLE_TYPE'] = vehicle_type
    os.environ['FUEL_TYPE'] = fuel_type
    os.environ['MIN_PRICE'] = str(min_price)
    os.environ['MAX_PRICE'] = str(max_price)
    os.environ['MIN_ENGINE_POWER'] = str(min_power)
    os.environ['MAX_ENGINE_POWER'] = str(max_power)
    os.environ['BASE_URL'] = 'https://www.mobile.bg/obiavi'
    os.environ['GENERAL_TYPE'] = 'avtomobili-dzhipove'
    
    # Configure custom logger for this thread
    logger = logging.getLogger(f"crawl_logger_{session_id}")
    logger.setLevel(logging.INFO)
    session_handler = SessionLogHandler(session_id)
    session_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(session_handler)
    
    try:
        session = CrawlSession.objects.get(id=session_id)
        logger.info(f"🚀 Starting crawl for {brand.upper()} {model.upper()}...")
        
        # Build search URL
        search_url = build_mobilebg_search_url(logger)
        
        # Validate URL
        if not validate_search_url(search_url, logger):
            logger.error("❌ Search URL validation failed. Please check brand, model, or fuel settings.")
            session.status = 'failed'
            session.end_time = timezone.now()
            session.save(update_fields=['status', 'end_time'])
            return
        
        # Get all listing links
        links = get_all_listing_links(search_url, delay=delay, max_pages=max_pages, logger=logger)
        links = list(links)
        
        if not links:
            logger.error("❌ No car links found. Crawler finished with 0 results.")
            session.status = 'completed'
            session.total_found = 0
            session.end_time = timezone.now()
            session.save(update_fields=['status', 'total_found', 'end_time'])
            return
            
        session.total_found = len(links)
        session.save(update_fields=['total_found'])
        logger.info(f"📊 Total of {len(links)} links found. Starting details extraction...")
        
        scraped_cars = []
        for i, link in enumerate(links, 1):
            # Check if user cancelled / stopped the crawl
            session.refresh_from_db()
            if session.status == 'stopped':
                logger.warning("🛑 Crawling session stopped by user.")
                break
                
            logger.info(f"[{i}/{len(links)}] Scraping listing: {link.split('/')[-1] if '/' in link else link}")
            
            try:
                car_info = extract_car_info_unified(link)
                if car_info:
                    # Save/Update CarListing in DB
                    price_bgn = car_info.get('Price_BGN')
                    price_eur = car_info.get('Price_EUR')
                    
                    if not price_eur and price_bgn:
                        try:
                            price_eur = round(float(price_bgn) / 1.95583, 2)
                        except (ValueError, TypeError):
                            pass
                    
                    listing, created = CarListing.objects.update_or_create(
                        link=link,
                        defaults={
                            'session': session,
                            'brand': car_info.get('Brand', brand),
                            'model': car_info.get('Model', model),
                            'production_date': car_info.get('Production Date'),
                            'price_eur': price_eur if price_eur not in ('', None) else None,
                            'price_bgn': None,
                            'engine': car_info.get('Engine'),
                            'fuel_type': car_info.get('Fuel Type', fuel_type),
                            'transmission': car_info.get('Transmission'),
                            'mileage': car_info.get('Mileage'),
                            'color': car_info.get('Color'),
                            'location': car_info.get('Location'),
                            'phone': car_info.get('Phone'),
                            'description': car_info.get('Описание'),
                            'extras': car_info.get('Car Extras'),
                        }
                    )
                    scraped_cars.append(car_info)
                    session.success_count += 1
                else:
                    session.fail_count += 1
            except Exception as e:
                logger.error(f"⚠️ Error scraping {link}: {e}")
                session.fail_count += 1
                
            session.processed_count = i
            session.save(update_fields=['processed_count', 'success_count', 'fail_count'])
            
            if delay > 0 and i < len(links):
                time.sleep(delay)
                
        # Session complete
        session.refresh_from_db()
        if session.status != 'stopped':
            session.status = 'completed'
            
        session.end_time = timezone.now()
        
        # Export to Excel
        if scraped_cars:
            excel_dir = Path("docs")
            excel_dir.mkdir(exist_ok=True)
            filename = f"docs/{brand}-{model}-{session_id.hex[:6]}.xlsx"
            excel_utils.export_to_excel(scraped_cars, filename, f"{brand.title()}-{model.title()}")
            session.excel_file_path = filename
            logger.info(f"💾 Scraped data exported to: {filename}")
            
        session.save(update_fields=['status', 'end_time', 'excel_file_path'])
        logger.info("🎯 Crawling session finished!")
        
    except Exception as e:
        logger.exception(f"💥 Session encountered a critical error: {e}")
        try:
            session = CrawlSession.objects.get(id=session_id)
            session.status = 'failed'
            session.end_time = timezone.now()
            session.save(update_fields=['status', 'end_time'])
        except:
            pass
    finally:
        ACTIVE_CRAWLS.pop(session_id, None)

def start_crawl_in_background(session_id, brand, model, vehicle_type, fuel_type, min_price, max_price, min_power, max_power, max_pages, delay):
    """Starts the crawler execution in a non-blocking background thread."""
    thread = threading.Thread(
        target=run_crawl_session,
        args=(session_id, brand, model, vehicle_type, fuel_type, min_price, max_price, min_power, max_power, max_pages, delay),
        daemon=True
    )
    ACTIVE_CRAWLS[session_id] = thread
    thread.start()
    return thread
