#!/usr/bin/env python3
"""
Test script for pagination functionality
Tests the web scraper's ability to crawl multiple pages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.web_scraper import get_all_listing_links
from modules.logger_config import setup_logging
from modules.url_builder import build_mobilebg_search_url


def test_pagination_detection():
    """Test pagination detection on mobile.bg"""
    print('=== TESTING PAGINATION DETECTION ===')
    
    import requests
    from bs4 import BeautifulSoup
    
    # Test the mobile.bg search page pagination
    search_url = 'https://www.mobile.bg/obiavi/avtomobili-dzhipove/mitsubishi/outlander/dzhip/benzinov?price=5000&price1=9000&engine_power=100&engine_power1=200'
    
    print(f'Testing URL: {search_url}')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        print(f'HTTP Status: {response.status_code}')
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for results info
        import re
        all_divs = soup.find_all('div')
        result_info = None
        
        for div in all_divs:
            div_text = div.get_text().strip()
            if re.search(r'\d+.*от.*общо.*\d+', div_text):
                result_info = div
                break
        
        if result_info:
            result_text = result_info.get_text()
            print(f'✅ Results info found: "{result_text.strip()}"')
            
            # Extract total count
            match = re.search(r'от общо (\d+)', result_text)
            if match:
                total_results = int(match.group(1))
                print(f'✅ Total results detected: {total_results}')
            else:
                print('❌ Could not parse total results')
                return False
        else:
            print('❌ No results info found')
            return False
            
        # Look for pagination elements
        pagination = soup.find('div', class_='pagination')
        if pagination:
            print('✅ Pagination div found')
            
            # Look for next page link
            next_links = pagination.find_all('a', href=True)
            next_found = False
            
            for link in next_links:
                link_text = link.get_text().strip().lower()
                if any(keyword in link_text for keyword in ['напред', 'next', '>', '»']):
                    href = link.get('href')
                    print(f'✅ Next page link found: "{link_text}" → {href}')
                    next_found = True
                    break
            
            if not next_found:
                print('❌ No next page link found')
                return False
                
        else:
            print('❌ No pagination div found')
            return False
        
        return True
        
    except Exception as e:
        print(f'❌ Error testing pagination: {e}')
        return False


def test_full_pagination():
    """Test full pagination crawling"""
    print('\n=== TESTING FULL PAGINATION CRAWLING ===')
    
    # Setup logging
    logger = setup_logging()
    
    # Test URL - known to have multiple pages
    search_url = 'https://www.mobile.bg/obiavi/avtomobili-dzhipove/mitsubishi/outlander/dzhip/benzinov?price=5000&price1=9000&engine_power=100&engine_power1=200'
    
    print(f'Testing full crawl with max 3 pages...')
    
    # Get all links with pagination
    links = get_all_listing_links(search_url, delay=0.5, max_pages=3, logger=logger)
    
    print(f'\n📊 CRAWLING RESULTS:')
    print(f'  Total links found: {len(links)}')
    print(f'  Expected: ~38 cars (based on previous tests)')
    
    # Verify we got a reasonable number of results
    if len(links) >= 30:  # Should be around 38, allow some variance
        print('✅ Full pagination test PASSED')
        return True
    else:
        print(f'❌ Full pagination test FAILED - only got {len(links)} links')
        return False


def test_url_builder_integration():
    """Test URL builder integration with pagination"""
    print('\n=== TESTING URL BUILDER INTEGRATION ===')
    
    try:
        # Load env and build URL
        from modules.config_manager import load_env_config
        load_env_config()
        
        search_url = build_mobilebg_search_url()
        print(f'✅ Built search URL: {search_url}')
        
        # Quick test - just get first page
        logger = setup_logging()
        links = get_all_listing_links(search_url, delay=0.5, max_pages=1, logger=logger)
        
        print(f'✅ Got {len(links)} links from first page')
        
        if len(links) > 0:
            print('✅ URL builder integration test PASSED')
            return True
        else:
            print('❌ URL builder integration test FAILED - no links found')
            return False
            
    except Exception as e:
        print(f'❌ Error testing URL builder integration: {e}')
        return False


if __name__ == '__main__':
    print('🧪 PAGINATION TEST SUITE')
    print('=' * 50)
    
    success1 = test_pagination_detection()
    success2 = test_full_pagination()
    success3 = test_url_builder_integration()
    
    print('\n' + '=' * 50)
    if success1 and success2 and success3:
        print('🎉 All pagination tests PASSED!')
    else:
        print('❌ Some pagination tests FAILED')
        sys.exit(1)