"""
Web Scraper Module for AutoGetCars Crawler
Handles web scraping and data extraction from mobile.bg
"""

import time
import math
import logging
import requests
from bs4 import BeautifulSoup


def get_all_listing_links(search_url, delay=1.0, max_pages=100, logger=None):
    """
    Crawl all result pages and collect car listing links.
    
    Args:
        search_url (str): The initial search URL
        delay (float): Delay between requests in seconds
        max_pages (int): Maximum number of pages to crawl
        logger (logging.Logger, optional): Logger instance
        
    Returns:
        set: Set of unique car listing URLs
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    links = set()
    total_results = None
    url = search_url
    page_num = 1
    start_time = time.time()
    
    logger.info(f"🔗 Search URL: {search_url}")
    
    while True:
        try:
            logger.info(f"📡 Fetching Page {page_num}: {url}")
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 404:
                logger.error(f"❌ Failed to fetch page {page_num}: HTTP 404")
                break
            elif response.status_code != 200:
                logger.error(f"❌ Failed to fetch page {page_num}: HTTP {response.status_code}")
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract total results on first page
            if page_num == 1:
                try:
                    # Look for results info in div with inline styles or any div containing results pattern
                    result_info = None
                    
                    # Try finding div with results pattern
                    import re
                    all_divs = soup.find_all('div')
                    for div in all_divs:
                        div_text = div.get_text().strip()
                        if re.search(r'\d+.*от.*общо.*\d+', div_text):
                            result_info = div
                            break
                    
                    if result_info:
                        result_text = result_info.get_text()
                        # Extract total from pattern like "1 - 20 от общо 38"
                        match = re.search(r'от общо (\d+)', result_text)
                        if match:
                            total_results = int(match.group(1))
                            estimated_pages = math.ceil(total_results / 20)
                            estimated_time = estimated_pages * delay
                            
                            logger.info("📊 SEARCH RESULTS SUMMARY:")
                            logger.info(f" 🎯 Total Results Found: {total_results} cars")
                            logger.info(f" 📄 Estimated Pages: {estimated_pages} pages (~20 cars per page)")
                            logger.info(f" ⏱️  Estimated Crawl Time: ~{estimated_time:.1f} seconds")
                except Exception as e:
                    logger.warning(f"Could not extract total results: {e}")
            
            # Find car listing links
            car_links = soup.find_all('a', href=True)
            page_links = set()
            
            for link in car_links:
                href = link.get('href')
                if href and '/obiava-' in href:
                    # Properly format the URL
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('//'):
                        full_url = 'https:' + href
                    elif href.startswith('/'):
                        full_url = 'https://www.mobile.bg' + href
                    else:
                        full_url = 'https://www.mobile.bg/' + href
                    
                    if full_url not in links:
                        page_links.add(full_url)
                        links.add(full_url)
            
            if page_links:
                progress = (len(links) / total_results * 100) if total_results else 0
                logger.info(f"  📄 Page {page_num}: Found {len(page_links)} links, {len(page_links)} new ({progress:.1f}% complete)")
            else:
                logger.warning(f"  📄 Page {page_num}: No car links found")
            
            # Find next page link
            next_link = None
            pagination = soup.find('div', class_='pagination')
            if pagination:
                next_links = pagination.find_all('a', href=True)
                for link in next_links:
                    link_text = link.get_text().strip().lower()
                    # Check for Bulgarian "Напред" (Next) or other next indicators
                    if any(keyword in link_text for keyword in ['next', 'напред', '>', '»', 'следваща']) or 'next' in link.get('class', []):
                        next_href = link.get('href')
                        if next_href:
                            # Properly format next page URL
                            if next_href.startswith('http'):
                                next_link = next_href
                            elif next_href.startswith('//'):
                                next_link = 'https:' + next_href
                            elif next_href.startswith('/'):
                                next_link = 'https://www.mobile.bg' + next_href
                            else:
                                next_link = 'https://www.mobile.bg/' + next_href
                            break
            
            # Check if we should continue
            if page_num >= max_pages:
                logger.info(f"🛑 Reached max_pages={max_pages}. Stopping.")
                break
                
            if not next_link:
                logger.info(f"🏁 No more pages found. Crawling complete!")
                break
                
            if not page_links:
                logger.info(f"🚫 No new links found on page {page_num}. Stopping.")
                break
            
            logger.info(f"Next page URL: {next_link}")
            url = next_link
            page_num += 1
            
            # Respectful delay
            if delay > 0:
                time.sleep(delay)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error on page {page_num}: {e}")
            break
        except Exception as e:
            logger.error(f"❌ Error processing page {page_num}: {e}")
            break
    
    if not links:
        logger.error("❌ No car links found. Exiting.")
        return set()
    
    elapsed_time = time.time() - start_time
    logger.info(f"🔗 LINK COLLECTION COMPLETE!")
    logger.info(f"  📊 Total Unique Links: {len(links)} cars")
    logger.info(f"  📄 Pages Processed: {page_num}")
    logger.info(f"  ⏱️  Total Collection Time: {elapsed_time:.1f} seconds")
    
    return links