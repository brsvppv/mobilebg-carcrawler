#!/usr/bin/env python3
"""
Test script for Excel structure verification
Tests Excel file structure, headers, and data integrity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openpyxl import load_workbook
from modules.config_manager import load_env_config, get_output_config


def test_excel_structure():
    """Test Excel structure and data integrity with the latest export"""
    print('📊 EXCEL STRUCTURE VERIFICATION TEST')
    print('=' * 50)
    
    load_env_config()
    config = get_output_config()
    excel_path = config.get('excel_path', 'docs/car-data.xlsx')
    
    if not os.path.exists(excel_path):
        print(f'❌ Excel file not found at {excel_path}!')
        return False
    
    try:
        print(f'📁 Opening: {excel_path}')
        
        wb = load_workbook(excel_path)
        print(f'📋 Available sheets: {wb.sheetnames}')
        
        # Test the first sheet (should be the latest)
        ws = wb[wb.sheetnames[0]]
        sheet_name = wb.sheetnames[0]
        
        print(f'\n--- Sheet: {sheet_name} ---')
        print(f'📊 Total rows: {ws.max_row} (including header)')
        print(f'📊 Total columns: {ws.max_column}')
        print(f'📊 Data rows: {ws.max_row - 1} cars')
        
        # Verify headers
        headers = [ws.cell(row=1, column=col).value for col in range(1, ws.max_column + 1)]
        expected_headers = [
            'Brand', 'Model', 'Production Date', 'Price_EUR', 'Price_BGN', 
            'Engine', 'Fuel Type', 'Transmission', 'Mileage', 'Color', 
            'Location', 'Phone', 'Link', 'Описание', 'Car Extras'
        ]
        
        print(f'\n📋 HEADER VERIFICATION:')
        headers_correct = True
        for i, (expected, actual) in enumerate(zip(expected_headers, headers), 1):
            match = expected == actual
            status = '✅' if match else '❌'
            print(f'  {i:2d}. {expected:<15} → {actual:<15} {status}')
            if not match:
                headers_correct = False
        
        # Verify we have exactly 15 columns (optimized structure)
        if ws.max_column == 15:
            print(f'\n✅ Column count correct: {ws.max_column} columns')
        else:
            print(f'\n❌ Column count incorrect: Expected 15, got {ws.max_column}')
            headers_correct = False
        
        # Sample data verification
        print(f'\n📊 SAMPLE DATA VERIFICATION:')
        data_correct = True
        sample_size = min(5, ws.max_row - 1)
        
        for row in range(2, 2 + sample_size):
            brand = ws.cell(row=row, column=1).value
            model = ws.cell(row=row, column=2).value
            prod_date = ws.cell(row=row, column=3).value
            price_eur = ws.cell(row=row, column=4).value
            price_bgn = ws.cell(row=row, column=5).value
            location = ws.cell(row=row, column=11).value
            
            print(f'\n  Car {row-1}: {brand} {model}')
            print(f'    📅 Production Date: "{prod_date}"')
            print(f'    💰 EUR: {price_eur} ({type(price_eur).__name__})')
            print(f'    💰 BGN: {price_bgn} ({type(price_bgn).__name__})')
            print(f'    📍 Location: {location}')
            
            # Verify data types
            if isinstance(price_eur, (int, float)) and isinstance(price_bgn, (int, float)):
                print('    ✅ Price data types correct')
            else:
                print('    ❌ Price data types incorrect')
                data_correct = False
            
            # Check production date format
            if prod_date and isinstance(prod_date, str):
                bulgarian_months = ['януари', 'февруари', 'март', 'април', 'май', 'юни', 
                                  'юли', 'август', 'септември', 'октомври', 'ноември', 'декември']
                if any(month in prod_date.lower() for month in bulgarian_months):
                    print('    ✅ Production date format correct')
                else:
                    print(f'    ⚠️  Production date format may be incomplete: "{prod_date}"')
            else:
                print('    ❌ Production date missing or invalid')
                data_correct = False
        
        wb.close()
        
        # Final result
        overall_success = headers_correct and data_correct
        
        print(f'\n📊 VERIFICATION RESULTS:')
        print(f'  📋 Headers: {"✅ PASS" if headers_correct else "❌ FAIL"}')
        print(f'  📊 Data: {"✅ PASS" if data_correct else "❌ FAIL"}')
        
        if overall_success:
            print('\n🎉 Excel structure verification PASSED!')
        else:
            print('\n❌ Excel structure verification FAILED!')
        
        return overall_success
        
    except Exception as e:
        print(f'❌ Error during Excel verification: {e}')
        return False


if __name__ == '__main__':
    success = test_excel_structure()
    sys.exit(0 if success else 1)