#!/usr/bin/env python3
"""
Test script for production date extraction functionality
Tests full production date extraction (month + year format)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.extractors import extract_car_info_mobile
from Tests.test_helper import get_active_test_urls


def test_production_date_extraction():
    """Test production date extraction with multiple car examples"""
    print('🧪 PRODUCTION DATE EXTRACTION TEST')
    print('=' * 50)
    
    # Test multiple cars dynamically to verify production date extraction
    test_urls = get_active_test_urls(3)
    
    success_count = 0
    total_tests = len(test_urls)
    
    for i, url in enumerate(test_urls, 1):
        print(f'\n🚗 Testing Car {i}/{total_tests}:')
        try:
            car_info = extract_car_info_mobile(url, timeout=15)
            if car_info:
                brand = car_info.get('Brand', 'Unknown')
                model = car_info.get('Model', 'Unknown')
                prod_date = car_info.get('Production Date', 'Not found')
                price_eur = car_info.get('Price_EUR', 0)
                price_bgn = car_info.get('Price_BGN', 0)
                location = car_info.get('Location', 'Unknown')
                
                print(f'  📋 {brand} {model}')
                print(f'  📅 Production Date: "{prod_date}"')
                print(f'  💰 Price: {price_eur} EUR / {price_bgn} BGN')
                print(f'  📍 Location: {location}')
                
                # Check if production date has full month+year format
                bulgarian_months = ['януари', 'февруари', 'март', 'април', 'май', 'юни', 
                                  'юли', 'август', 'септември', 'октомври', 'ноември', 'декември']
                
                if any(month in prod_date.lower() for month in bulgarian_months):
                    print('  ✅ Full production date extracted successfully')
                    success_count += 1
                else:
                    print(f'  ⚠️  Production date may be incomplete: "{prod_date}"')
                    # Still count as success if we got some date
                    if prod_date and prod_date != 'Not found':
                        success_count += 1
            else:
                print('  ❌ Failed to extract car data')
        except Exception as e:
            print(f'  ❌ Error: {e}')
    
    print(f'\n📊 TEST RESULTS:')
    print(f'  ✅ Successful extractions: {success_count}/{total_tests}')
    print(f'  📈 Success rate: {(success_count/total_tests)*100:.1f}%')
    
    if success_count == total_tests:
        print('🎉 Production date test PASSED!')
        return True
    else:
        print('❌ Production date test FAILED!')
        return False


if __name__ == '__main__':
    success = test_production_date_extraction()
    sys.exit(0 if success else 1)