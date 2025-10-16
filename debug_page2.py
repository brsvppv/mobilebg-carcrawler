#!/usr/bin/env python3
"""
Debug pagination - test page 2 to see if it's working
"""

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_page_2():
    """Test page 2 directly"""
    page_2_url = "https://www.mobile.bg/obiavi/avtomobili-dzhipove/audi/a4/sedan/dizelov/p-2?price=8000&price1=35000&engine_power=120&engine_power1=250"
    
    print(f"🔗 Testing Page 2: {page_2_url}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(page_2_url, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch page 2: HTTP {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for results info
    print("\n🔍 Looking for results info on page 2...")
    all_divs = soup.find_all('div')
    for div in all_divs:
        div_text = div.get_text().strip()
        if re.search(r'\d+.*от.*общо.*\d+', div_text):
            print(f"📊 Results info: {div_text}")
            break
    
    # Look for car listing links
    print("\n🚗 Looking for car listing links on page 2...")
    car_links = soup.find_all('a', href=True)
    listing_count = 0
    unique_links = set()
    
    for link in car_links:
        href = link.get('href')
        if href and '/obiava-' in href:
            listing_count += 1
            unique_links.add(href)
            if listing_count <= 5:  # Show first 5 links
                print(f"  🔗 Link {listing_count}: {href}")
    
    print(f"📊 Total car links found on page 2: {listing_count}")
    print(f"📊 Unique car links on page 2: {len(unique_links)}")
    
    # Look for pagination on page 2
    print("\n📄 Looking for pagination on page 2...")
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

if __name__ == "__main__":
    test_page_2()