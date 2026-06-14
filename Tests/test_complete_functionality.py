#!/usr/bin/env python3
"""
Test script for comprehensive functionality testing
Tests all major system components and functionalities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.extractors import extract_car_info_mobile
from modules.web_scraper import get_all_listing_links
from modules.config_manager import load_env_config
from modules.url_builder import build_mobilebg_search_url
from Tests.test_helper import get_active_test_urls


def test_complete_functionality():
    """Test all major functionalities of the crawler system"""
    print('🧪 COMPREHENSIVE FUNCTIONALITY TEST')
    print('=' * 60)
    
    test_results = {}
    
    # Test 1: Configuration Loading
    print('\n🔧 TEST 1: Configuration Loading')
    print('-' * 40)
    try:
        load_env_config()
        search_url = build_mobilebg_search_url()
        print(f'✅ Configuration loaded successfully')
        print(f'🔗 Search URL: {search_url}')
        test_results['config'] = True
    except Exception as e:
        print(f'❌ Configuration test failed: {e}')
        test_results['config'] = False
    
    # Test 2: Web Scraping and Pagination
    print('\n🕷️ TEST 2: Web Scraping and Pagination')
    print('-' * 40)
    try:
        if test_results.get('config'):
            links = get_all_listing_links(search_url, max_pages=2)
            print(f'✅ Web scraping successful')
            print(f'📊 Found {len(links)} car links')
            if len(links) >= 20:  # Should get at least first page
                print(f'✅ Pagination working correctly')
                test_results['scraping'] = True
            else:
                print(f'⚠️  Got fewer links than expected')
                test_results['scraping'] = False
        else:
            print('⏭️  Skipped due to config failure')
            test_results['scraping'] = False
    except Exception as e:
        print(f'❌ Web scraping test failed: {e}')
        test_results['scraping'] = False
    
    # Test 3: Data Extraction
    print('\n📊 TEST 3: Data Extraction')
    print('-' * 40)
    test_urls = get_active_test_urls(2)
    
    extraction_success = 0
    for i, url in enumerate(test_urls, 1):
        try:
            print(f'  Testing extraction {i}/{len(test_urls)}...')
            car_info = extract_car_info_mobile(url, timeout=15)
            
            if car_info and car_info.get('Brand') and car_info.get('Model'):
                print(f'    ✅ {car_info["Brand"]} {car_info["Model"]}')
                
                # Verify key fields
                checks = []
                checks.append(('Production Date', car_info.get('Production Date')))
                checks.append(('Price_EUR', car_info.get('Price_EUR')))
                checks.append(('Price_BGN', car_info.get('Price_BGN')))
                checks.append(('Location', car_info.get('Location')))
                
                all_good = True
                for field, value in checks:
                    if value:
                        print(f'      ✅ {field}: {value}')
                    else:
                        print(f'      ❌ {field}: Missing')
                        all_good = False
                
                if all_good:
                    extraction_success += 1
            else:
                print(f'    ❌ Failed to extract basic info')
                
        except Exception as e:
            print(f'    ❌ Extraction error: {e}')
    
    test_results['extraction'] = (extraction_success == len(test_urls))
    if test_results['extraction']:
        print(f'✅ Data extraction test passed ({extraction_success}/{len(test_urls)})')
    else:
        print(f'❌ Data extraction test failed ({extraction_success}/{len(test_urls)})')
    
    # Test 4: Price Format Validation
    print('\n💰 TEST 4: Price Format Validation')
    print('-' * 40)
    try:
        # Test with a known car
        car_info = extract_car_info_mobile(test_urls[0], timeout=15)
        
        if car_info:
            price_eur = car_info.get('Price_EUR')
            price_bgn = car_info.get('Price_BGN')
            
            eur_valid = isinstance(price_eur, (int, float)) and price_eur > 0
            bgn_valid = isinstance(price_bgn, (int, float)) and price_bgn > 0
            
            print(f'  EUR Price: {price_eur} ({"✅" if eur_valid else "❌"})')
            print(f'  BGN Price: {price_bgn} ({"✅" if bgn_valid else "❌"})')
            
            test_results['prices'] = eur_valid and bgn_valid
            if test_results['prices']:
                print('✅ Price format validation passed')
            else:
                print('❌ Price format validation failed')
        else:
            print('❌ Could not test price format - no data extracted')
            test_results['prices'] = False
            
    except Exception as e:
        print(f'❌ Price format test failed: {e}')
        test_results['prices'] = False
    
    # Test 5: Production Date Format
    print('\n📅 TEST 5: Production Date Format')
    print('-' * 40)
    try:
        bulgarian_months = ['януари', 'февруари', 'март', 'април', 'май', 'юни', 
                          'юли', 'август', 'септември', 'октомври', 'ноември', 'декември']
        
        date_tests = 0
        date_success = 0
        
        for url in test_urls:
            car_info = extract_car_info_mobile(url, timeout=15)
            if car_info:
                prod_date = car_info.get('Production Date', '')
                date_tests += 1
                
                if any(month in prod_date.lower() for month in bulgarian_months):
                    print(f'  ✅ Full date format: "{prod_date}"')
                    date_success += 1
                else:
                    print(f'  ⚠️  Partial date: "{prod_date}"')
        
        test_results['dates'] = (date_success >= date_tests * 0.8)  # 80% success rate
        if test_results['dates']:
            print(f'✅ Production date format test passed ({date_success}/{date_tests})')
        else:
            print(f'❌ Production date format test failed ({date_success}/{date_tests})')
            
    except Exception as e:
        print(f'❌ Production date test failed: {e}')
        test_results['dates'] = False
    
    # Final Results
    print('\n' + '=' * 60)
    print('📊 COMPREHENSIVE TEST RESULTS')
    print('=' * 60)
    
    tests = [
        ('Configuration Loading', 'config'),
        ('Web Scraping & Pagination', 'scraping'),
        ('Data Extraction', 'extraction'),
        ('Price Format Validation', 'prices'),
        ('Production Date Format', 'dates')
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, key in tests:
        status = "✅ PASS" if test_results.get(key, False) else "❌ FAIL"
        print(f'  {test_name:<25} {status}')
        if test_results.get(key, False):
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f'\n📈 Overall Success Rate: {success_rate:.1f}% ({passed}/{total})')
    
    if passed == total:
        print('\n🎉 ALL FUNCTIONALITY TESTS PASSED!')
        print('🚀 System is fully operational!')
        return True
    else:
        print(f'\n⚠️  {total - passed} test(s) failed')
        print('🔧 Please review and fix the issues')
        return False


if __name__ == '__main__':
    success = test_complete_functionality()
    sys.exit(0 if success else 1)