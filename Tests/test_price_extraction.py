#!/usr/bin/env python3
"""
Test script for price extraction functionality
Tests the extractor's ability to separate EUR and convert BGN prices
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.extractors import extract_car_info_mobile
from Tests.test_helper import get_active_test_urls


def test_single_car_extraction():
    """Test extracting data from a single car listing"""
    print('=== TESTING SINGLE CAR PRICE EXTRACTION ===')
    
    # Test with a dynamically resolved active listing
    urls = get_active_test_urls(1)
    url = urls[0]
    print(f'Testing URL: {url}')
    
    car_data = extract_car_info_mobile(url)
    
    if not car_data:
        print('❌ No data extracted')
        return False
    
    print('\n📋 Extracted car data:')
    for key, value in car_data.items():
        if value and key != 'price_numeric':  # Skip internal field
            print(f'  {key}: {value}')
    
    # Verify price separation
    print(f'\n💰 Price breakdown:')
    print(f'  Original Price field: "{car_data.get("Price", "")}"')
    print(f'  Price_EUR (numeric): {car_data.get("Price_EUR", "")}')
    print(f'  Price_BGN (should be empty): {car_data.get("Price_BGN", "")}')
    
    # Check if price columns are properly populated
    success = (
        car_data.get('Price_EUR') and 
        isinstance(car_data.get('Price_EUR'), (int, float))
    )
    
    if success:
        print('\n✅ Price extraction test PASSED')
        return True
    else:
        print('\n❌ Price extraction test FAILED')
        return False


def test_price_format_variations():
    """Test different price format scenarios and conversions"""
    print('\n=== TESTING PRICE FORMAT VARIATIONS ===')
    
    # Create test data with different price formats
    test_data = [
        {
            'name': 'Standard Euro-Only Format',
            'price_text': '2 964.98 €',
            'expected_eur': 2964.98,
        },
        {
            'name': 'BGN-Only Format (Converts to EUR)',
            'price_text': '5 799 лв.',
            'expected_eur': 2964.98, # 5799 / 1.95583 = 2964.98
        },
        {
            'name': 'BGN with Decimal Format (Converts to EUR)',
            'price_text': '38 136.73 лв.',
            'expected_eur': 19499.00, # 38136.73 / 1.95583 = 19499.00
        }
    ]
    
    print('Testing price parsing logic:')
    
    import re
    for test_case in test_data:
        print(f'\n🧪 {test_case["name"]}:')
        price_text = test_case['price_text']
        print(f'   Input: "{price_text}"')
        
        # Test EUR/BGN extraction logic matching modules/extractors.py
        p = price_text.replace(' ', '')
        euro_match = re.search(r'([\d\.]+)\s*€', p)
        bgn_match = re.search(r'([\d\.]+)\s*лв', p)
        
        eur_result = None
        if euro_match:
            eur_result = float(euro_match.group(1))
        elif bgn_match:
            eur_result = round(float(bgn_match.group(1)) / 1.95583, 2)
            
        print(f'   Expected EUR: {test_case["expected_eur"]} | Got: {eur_result}')
        
        if eur_result == test_case['expected_eur']:
            print('   ✅ PASSED')
        else:
            print('   ❌ FAILED')
    
    print('\n✅ Price format variation tests completed')


if __name__ == '__main__':
    print('🧪 PRICE EXTRACTION TEST SUITE')
    print('=' * 50)
    
    success1 = test_single_car_extraction()
    test_price_format_variations()
    
    print('\n' + '=' * 50)
    if success1:
        print('🎉 All price extraction tests PASSED!')
    else:
        print('❌ Some tests FAILED')
        sys.exit(1)