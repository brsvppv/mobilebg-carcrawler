#!/usr/bin/env python3
"""
Master test runner - runs all test scripts
Provides a unified interface to run all crawler tests
"""

import sys
import os
import subprocess
import time

def run_test_script(script_path, script_name):
    """Run a test script and return success status"""
    print(f'\n🧪 Running {script_name}...')
    print('=' * 60)
    
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the test script with project root in PYTHONPATH
        env = dict(os.environ)
        env['PYTHONPATH'] = project_root
        result = subprocess.run([
            sys.executable, script_path
        ], cwd=project_root, env=env, capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f'✅ {script_name} PASSED')
            return True
        else:
            print(f'❌ {script_name} FAILED (exit code: {result.returncode})')
            return False
            
    except Exception as e:
        print(f'❌ Error running {script_name}: {e}')
        return False


def main():
    """Run all test scripts"""
    print('🧪 AUTOGETCARS CRAWLER - COMPLETE TEST SUITE')
    print('=' * 70)
    print('🚀 Running all tests to verify system functionality...')
    
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define test scripts in order of execution
    test_scripts = [
        ('test_price_extraction.py', 'Price Extraction Tests'),
        ('test_excel_export.py', 'Excel Export Tests'),
        ('test_pagination.py', 'Pagination Tests'),
        ('test_complete_system.py', 'Complete System Tests'),
        ('test_production_date_extraction.py', 'Production Date Tests'),
        ('test_excel_structure.py', 'Excel Structure Tests'),
        ('test_complete_functionality.py', 'Complete Functionality Tests'),
        ('test_main_crawler_execution.py', 'Main Crawler Execution Tests')
    ]
    
    results = []
    start_time = time.time()
    
    for script_file, script_name in test_scripts:
        script_path = os.path.join(tests_dir, script_file)
        
        if os.path.exists(script_path):
            success = run_test_script(script_path, script_name)
            results.append((script_name, success))
        else:
            print(f'⚠️ Test script not found: {script_path}')
            results.append((script_name, False))
    
    # Summary
    elapsed_time = time.time() - start_time
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print('\n' + '=' * 70)
    print('📊 TEST SUITE SUMMARY')
    print('=' * 70)
    
    for script_name, success in results:
        status = '✅ PASSED' if success else '❌ FAILED'
        print(f'  {script_name:<30} {status}')
    
    print(f'\n⏱️ Total execution time: {elapsed_time:.1f} seconds')
    print(f'📈 Tests passed: {passed}/{total} ({passed/total*100:.1f}%)')
    
    if passed == total:
        print('\n🎉 ALL TESTS PASSED! 🚀')
        print('✨ The AutoGetCars Crawler is fully functional!')
        print('\n📋 System Features Verified:')
        print('  ✅ Price extraction with EUR/BGN separation')
        print('  ✅ Excel auto-creation from .env configuration')
        print('  ✅ Multi-page pagination crawling')
        print('  ✅ Complete end-to-end workflow')
        print('  ✅ Error handling and edge cases')
        print('\n🚀 Ready for production use!')
        sys.exit(0)
    else:
        print(f'\n❌ {total - passed} TEST(S) FAILED')
        print('🔧 Please check the failed tests and fix any issues.')
        sys.exit(1)


if __name__ == '__main__':
    main()