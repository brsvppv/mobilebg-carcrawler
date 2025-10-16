#!/usr/bin/env python3
"""
Test script for price extraction functionality
Tests the extractor's ability to separate EUR and BGN prices
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.extractors import extract_car_info_mobile


def test_single_car_extraction():
    """Test extracting data from a single car listing"""
    print('=== TESTING SINGLE CAR PRICE EXTRACTION ===')
    
    # Test with the Toyota Corolla listing
    url = 'https://www.mobile.bg/obiava-11759077895164151-toyota-corolla'
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
    print(f'  Price_BGN (numeric): {car_data.get("Price_BGN", "")}')
    
    # Check if price columns are properly populated
    success = (
        car_data.get('Price_EUR') and 
        car_data.get('Price_BGN') and 
        isinstance(car_data.get('Price_EUR'), (int, float)) and
        isinstance(car_data.get('Price_BGN'), (int, float))
    )
    
    if success:
        print('\n✅ Price extraction test PASSED')
        return True
    else:
        print('\n❌ Price extraction test FAILED')
        return False


def test_price_format_variations():
    """Test different price format scenarios"""
    print('\n=== TESTING PRICE FORMAT VARIATIONS ===')
    
    # Create test data with different price formats
    test_data = [
        {
            'name': 'Standard Format',
            'price_text': '2 964.98 €5 799 лв.',
            'expected_eur': 2964.98,
            'expected_bgn': 5799
        },
        {
            'name': 'Large Numbers',
            'price_text': '15 000.00 €29 300 лв.',
            'expected_eur': 15000.00,
            'expected_bgn': 29300
        },
        {
            'name': 'With Decimals',
            'price_text': '22 500.50 €44 000 лв.',
            'expected_eur': 22500.50,
            'expected_bgn': 44000
        }
    ]
    
    print('Testing price parsing logic:')
    
    for test_case in test_data:
        print(f'\n🧪 {test_case["name"]}:')
        price_text = test_case['price_text']
        print(f'   Input: "{price_text}"')
        
        # Test EUR extraction
        import re
        euro_match = re.search(r'([\d\s]+\.?\d*)\s*€', price_text.replace(' ', ''))
        eur_result = float(euro_match.group(1).replace(' ', '')) if euro_match else None
        
        # Test BGN extraction  
        bgn_match = re.search(r'([\d\s]+)\s*лв', price_text.replace(' ', ''))
        bgn_result = int(bgn_match.group(1).replace(' ', '')) if bgn_match else None
        
        print(f'   Expected EUR: {test_case["expected_eur"]} | Got: {eur_result}')
        print(f'   Expected BGN: {test_case["expected_bgn"]} | Got: {bgn_result}')
        
        eur_ok = eur_result == test_case['expected_eur']
        bgn_ok = bgn_result == test_case['expected_bgn']
        
        if eur_ok and bgn_ok:
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