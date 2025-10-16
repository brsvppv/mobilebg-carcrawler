#!/usr/bin/env python3
"""
Test script for main crawler execution
Tests the complete crawler workflow end-to-end
"""

import sys
import os
import subprocess
import time
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_main_crawler_execution():
    """Test the main crawler script execution"""
    print('🚀 MAIN CRAWLER EXECUTION TEST')
    print('=' * 50)
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    crawler_script = os.path.join(project_root, 'crawler.py')
    venv_python = os.path.join(project_root, '.venv', 'bin', 'python')
    
    print(f'📁 Project root: {project_root}')
    print(f'🐍 Python executable: {venv_python}')
    print(f'🕷️ Crawler script: {crawler_script}')
    
    # Check if files exist
    if not os.path.exists(crawler_script):
        print('❌ Crawler script not found!')
        return False
    
    if not os.path.exists(venv_python):
        print('❌ Virtual environment Python not found!')
        return False
    
    print('\n🔄 Executing main crawler...')
    print('-' * 30)
    
    try:
        # Run the crawler with a timeout
        start_time = time.time()
        
        # Execute the crawler
        result = subprocess.run(
            [venv_python, crawler_script],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f'⏱️  Execution time: {execution_time:.1f} seconds')
        print(f'📤 Return code: {result.returncode}')
        
        # Check if execution was successful
        if result.returncode == 0:
            print('✅ Crawler executed successfully!')
            
            # Parse output for key metrics
            output = result.stdout
            error_output = result.stderr
            
            if error_output:
                print(f'⚠️  Stderr output: {error_output[:200]}...')
            
            # Look for success indicators in output
            success_indicators = [
                ('Cars exported', 'cars to:'),
                ('Extraction completed', 'Successful Extractions'),
                ('Excel created', 'Exported')
            ]
            
            indicators_found = 0
            
            print(f'\n📊 SUCCESS INDICATORS:')
            for description, indicator in success_indicators:
                found = indicator in output
                status = '✅' if found else '❌'
                print(f'  {description}: {status}')
                if found:
                    indicators_found += 1
            
            # Extract key metrics from output
            if 'Total Unique Links:' in output:
                links_match = re.search(r'Total Unique Links: (\d+)', output)
                if links_match:
                    links_count = links_match.group(1)
                    print(f'🔗 Links found: {links_count}')
            
            if 'Successful Extractions:' in output:
                extractions_match = re.search(r'Successful Extractions: (\d+)', output)
                if extractions_match:
                    extractions_count = extractions_match.group(1)
                    print(f'📊 Extractions: {extractions_count}')
            
            if 'Exported' in output and 'cars to:' in output:
                export_match = re.search(r'Exported (\d+) cars to:', output)
                if export_match:
                    exported_count = export_match.group(1)
                    print(f'💾 Exported: {exported_count} cars')
            
            # Check if Excel file was created
            excel_path = os.path.join(project_root, 'docs', 'car-data.xlsx')
            if os.path.exists(excel_path):
                file_size = os.path.getsize(excel_path)
                print(f'📁 Excel file created: {file_size} bytes')
                
                # Verify Excel file has content
                if file_size > 5000:  # Reasonable file size
                    print('✅ Excel file has substantial content')
                    excel_success = True
                else:
                    print('⚠️  Excel file seems too small')
                    excel_success = False
            else:
                print('❌ Excel file not created')
                excel_success = False
            
            # Overall success criteria
            overall_success = (
                result.returncode == 0 and
                indicators_found >= 2 and
                excel_success and
                execution_time < 120  # Reasonable execution time (2 minutes)
            )
            
            if overall_success:
                print('\n🎉 Main crawler execution test PASSED!')
                return True
            else:
                print('\n⚠️  Main crawler execution had issues')
                return False
                
        else:
            print(f'❌ Crawler execution failed with return code: {result.returncode}')
            if result.stderr:
                print(f'Error output: {result.stderr}')
            return False
            
    except subprocess.TimeoutExpired:
        print('❌ Crawler execution timed out (>2 minutes)')
        return False
    except Exception as e:
        print(f'❌ Error executing crawler: {e}')
        return False


def test_quick_extraction_sample():
    """Test a quick sample of data extraction without full crawl"""
    print('\n🧪 QUICK EXTRACTION SAMPLE TEST')
    print('=' * 50)
    
    from modules.extractors import extract_car_info_mobile
    
    # Test with 2 known URLs for speed
    test_urls = [
        'https://www.mobile.bg/obiava-21748341999589220-mitsubishi-outlander-2-4-awd-sheytsariya',
        'https://www.mobile.bg/obiava-11759077895164151-toyota-corolla'
    ]
    
    success_count = 0
    
    for i, url in enumerate(test_urls, 1):
        print(f'\n🚗 Testing car {i}/{len(test_urls)}...')
        try:
            car_info = extract_car_info_mobile(url, timeout=10)
            
            if car_info and car_info.get('Brand'):
                brand = car_info.get('Brand', 'Unknown')
                model = car_info.get('Model', 'Unknown')
                prod_date = car_info.get('Production Date', 'N/A')
                price_eur = car_info.get('Price_EUR', 0)
                price_bgn = car_info.get('Price_BGN', 0)
                
                print(f'  ✅ {brand} {model}')
                print(f'    📅 Date: {prod_date}')
                print(f'    💰 Price: {price_eur}€ / {price_bgn}лв')
                
                success_count += 1
            else:
                print(f'  ❌ Failed to extract data')
                
        except Exception as e:
            print(f'  ❌ Error: {e}')
    
    success_rate = (success_count / len(test_urls)) * 100
    print(f'\n📊 Quick test results: {success_count}/{len(test_urls)} ({success_rate:.1f}%)')
    
    return success_count == len(test_urls)


if __name__ == '__main__':
    print('🧪 CRAWLER EXECUTION TESTS')
    print('=' * 60)
    
    # Run quick test first
    quick_success = test_quick_extraction_sample()
    
    # Run main crawler test
    main_success = test_main_crawler_execution()
    
    overall_success = quick_success and main_success
    
    print('\n' + '=' * 60)
    print('📊 EXECUTION TEST SUMMARY')
    print('=' * 60)
    print(f'  Quick Extraction Test:  {"✅ PASS" if quick_success else "❌ FAIL"}')
    print(f'  Main Crawler Test:      {"✅ PASS" if main_success else "❌ FAIL"}')
    print(f'  Overall Result:         {"✅ PASS" if overall_success else "❌ FAIL"}')
    
    if overall_success:
        print('\n🎉 ALL EXECUTION TESTS PASSED!')
    else:
        print('\n❌ Some execution tests failed')
    
    sys.exit(0 if overall_success else 1)