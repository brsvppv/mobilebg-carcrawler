# MobileBG CarCrawler - Test Suite

This folder contains comprehensive test scripts to verify the functionality of the MobileBG CarCrawler system.

## 🧪 Test Scripts

### 1. `test_price_extraction.py`
Tests the price extraction functionality:
- Single car data extraction
- EUR/BGN price separation
- Price format variations
- Data type validation

### 2. `test_excel_export.py` 
Tests Excel export functionality:
- Auto-creation of Excel files from .env config
- Excel file structure verification
- New sheet creation
- Price columns validation

### 3. `test_pagination.py`
Tests pagination crawling:
- Pagination detection on mobile.bg
- Multi-page crawling
- URL builder integration
- Results count parsing

### 4. `test_complete_system.py`
Tests end-to-end system functionality:
- Complete crawler workflow
- Error handling
- Performance verification
- System integration

### 5. `run_all_tests.py`
Master test runner that executes all test scripts and provides a summary.

## 🚀 Running Tests

### Run Individual Tests
```bash
# Price extraction tests
python Tests/test_price_extraction.py

# Excel export tests  
python Tests/test_excel_export.py

# Pagination tests
python Tests/test_pagination.py

# Complete system tests
python Tests/test_complete_system.py
```

### Run All Tests
```bash
# Run complete test suite
python Tests/run_all_tests.py
```

## 📊 Test Coverage

The test suite covers:
- ✅ Price extraction with EUR/BGN separation
- ✅ Excel file auto-creation and structure
- ✅ Multi-page pagination crawling  
- ✅ Data extraction accuracy
- ✅ Error handling and edge cases
- ✅ Configuration management
- ✅ End-to-end workflow validation

## 🎯 Expected Results

When all tests pass, you should see:
- Price extraction working with separate EUR/BGN columns
- Excel files auto-created in `docs/` directory  
- All 38+ cars fetched from mobile.bg search results
- Proper table formatting with 16 columns
- 100% success rate for data extraction

## 🔧 Troubleshooting

If tests fail:
1. Check internet connectivity for mobile.bg access
2. Verify `.env` file configuration is correct
3. Ensure all required Python packages are installed
4. Check that the `docs/` directory can be created/written to

## 📝 Test Data

Tests use both:
- **Live data**: Real mobile.bg car listings
- **Mock data**: Sample car data for structure validation

This ensures tests work both online and offline where applicable.