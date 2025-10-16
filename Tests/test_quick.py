#!/usr/bin/env python3
"""
Quick Test Runner - Run specific test categories
Allows running targeted tests without the full suite
"""

import sys
import os
import subprocess

def run_test(test_name, test_file):
    """Run a single test and return result"""
    print(f'🧪 Running {test_name}...')
    print('=' * 50)
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_path = os.path.join(project_root, 'Tests', test_file)
    
    try:
        result = subprocess.run([
            sys.executable, test_path
        ], cwd=project_root)
        
        if result.returncode == 0:
            print(f'✅ {test_name} PASSED\n')
            return True
        else:
            print(f'❌ {test_name} FAILED\n')
            return False
    except Exception as e:
        print(f'❌ Error running {test_name}: {e}\n')
        return False


def main():
    """Main function with test categories"""
    if len(sys.argv) < 2:
        print('🧪 QUICK TEST RUNNER')
        print('=' * 30)
        print('Usage: python test_quick.py <category>')
        print('\nAvailable test categories:')
        print('  core         - Core functionality (price, extraction, excel)')
        print('  advanced     - Advanced features (production dates, structure)')
        print('  system       - System tests (pagination, full workflow)')
        print('  execution    - Main crawler execution test')
        print('  all          - Run all tests')
        sys.exit(1)
    
    category = sys.argv[1].lower()
    
    test_categories = {
        'core': [
            ('Price Extraction', 'test_price_extraction.py'),
            ('Excel Export', 'test_excel_export.py'),
            ('Complete System', 'test_complete_system.py')
        ],
        'advanced': [
            ('Production Date Extraction', 'test_production_date_extraction.py'),
            ('Excel Structure Verification', 'test_excel_structure.py'),
            ('Complete Functionality', 'test_complete_functionality.py')
        ],
        'system': [
            ('Pagination', 'test_pagination.py'),
            ('Complete System Workflow', 'test_complete_system.py')
        ],
        'execution': [
            ('Main Crawler Execution', 'test_main_crawler_execution.py')
        ],
        'all': [
            ('Price Extraction', 'test_price_extraction.py'),
            ('Excel Export', 'test_excel_export.py'),
            ('Pagination', 'test_pagination.py'),
            ('Complete System', 'test_complete_system.py'),
            ('Production Date', 'test_production_date_extraction.py'),
            ('Excel Structure', 'test_excel_structure.py'),
            ('Complete Functionality', 'test_complete_functionality.py'),
            ('Main Crawler Execution', 'test_main_crawler_execution.py')
        ]
    }
    
    if category not in test_categories:
        print(f'❌ Unknown category: {category}')
        print('Available categories: core, advanced, system, execution, all')
        sys.exit(1)
    
    tests = test_categories[category]
    
    print(f'🧪 RUNNING {category.upper()} TESTS')
    print('=' * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, test_file in tests:
        success = run_test(test_name, test_file)
        if success:
            passed += 1
    
    print('=' * 50)
    print('📊 TEST RESULTS')
    print('=' * 50)
    print(f'  Tests passed: {passed}/{total} ({(passed/total)*100:.1f}%)')
    
    if passed == total:
        print(f'\n🎉 ALL {category.upper()} TESTS PASSED!')
    else:
        print(f'\n❌ {total - passed} test(s) failed')
    
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()