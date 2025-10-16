#!/usr/bin/env python3
"""
Debug pagination issues - test script to see why we're only getting first 20 results
"""

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.config_manager import load_env_config
from modules.logger_config import setup_logging
from modules.url_builder import build_mobilebg_search_url

def debug_pagination():
    """Debug pagination to see what's happening"""
    # Load configuration
    load_env_config()
    
    # Setup logging
    logger = setup_logging()
    
    # Build search URL
    search_url = build_mobilebg_search_url(logger)
    
    print(f"🔗 Testing URL: {search_url}")
    
    # Test first page
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(search_url, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch page: HTTP {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for results info
    print("\n🔍 Looking for results info...")
    all_divs = soup.find_all('div')
    for div in all_divs:
        div_text = div.get_text().strip()
        if re.search(r'\d+.*от.*общо.*\d+', div_text):
            print(f"📊 Results info: {div_text}")
            
            # Extract total from pattern like "1 - 20 от общо 38"
            match = re.search(r'от общо (\d+)', div_text)
            if match:
                total_results = int(match.group(1))
                print(f"🎯 Total results: {total_results}")
                break
    
    # Look for car listing links
    print("\n🚗 Looking for car listing links...")
    car_links = soup.find_all('a', href=True)
    listing_count = 0
    
    for link in car_links:
        href = link.get('href')
        if href and '/obiava-' in href:
            listing_count += 1
            if listing_count <= 5:  # Show first 5 links
                print(f"  🔗 Link {listing_count}: {href}")
    
    print(f"📊 Total car links found on page 1: {listing_count}")
    
    # Look for pagination
    print("\n📄 Looking for pagination...")
    pagination = soup.find('div', class_='pagination')
    if pagination:
        print("✅ Pagination div found!")
        next_links = pagination.find_all('a', href=True)
        print(f"🔗 Found {len(next_links)} pagination links:")
        
        for i, link in enumerate(next_links):
            link_text = link.get_text().strip()
            href = link.get('href')
            print(f"  {i+1}. Text: '{link_text}' -> {href}")
            
            # Check for next indicators
            if any(keyword in link_text.lower() for keyword in ['next', 'напред', '>', '»', 'следваща']):
                print(f"    ✅ This looks like a NEXT link!")
    else:
        print("❌ No pagination div found!")
        
        # Look for any pagination alternatives
        print("🔍 Looking for alternative pagination...")
        
        # Look for any links that might be pagination
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            text = link.get_text().strip()
            if 'page=' in href or any(word in text.lower() for word in ['next', 'напред', 'следваща']):
                print(f"  📄 Possible pagination link: '{text}' -> {href}")

if __name__ == "__main__":
    debug_pagination()