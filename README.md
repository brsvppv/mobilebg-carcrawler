# 🚗 MobileBG CarCrawler

**Version 1.0** | *October 2025*

A powerful, comprehensive web scraper specifically designed for mobile.bg (Bulgarian car marketplace). Built for market research, price analysis, and automotive data collection with professional-grade features and extensive test coverage.

## ✨ Key Features

### 🎯 **Core Functionality**
- **🔍 Multi-page Crawling**: Automatically crawls all available pages (e.g., 38/38 cars)
- **💰 Separate Price Columns**: EUR and BGN prices in dedicated numeric columns
- **📅 Production Date Extraction**: Full Bulgarian date format (e.g., "януари 2006")
- **📊 Excel Auto-Creation**: Formatted Excel files with 15 optimized columns
- **🌍 Location Detection**: Multiple extraction methods for Bulgarian cities
- **⚡ Performance Optimized**: Configurable delays and batch processing

### 🛡️ **Reliability & Testing**
- **🧪 Comprehensive Test Suite**: 8 test categories with 100% pass rate
- **📋 Error Handling**: Graceful handling of invalid URLs and missing data
- **📝 Detailed Logging**: Session logs with progress tracking and analytics
- **⚙️ Configuration Management**: Environment-based setup with `.env` files

### 📈 **Data Quality**
- **🎯 High Accuracy**: 100% extraction success rate
- **📊 Rich Data Fields**: 15 data columns including specifications and contact info
- **🔄 Real-time Validation**: URL and data validation before processing
- **💾 Auto-Export**: Excel files with proper formatting and data types

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.8+** installed
- **Internet connection** for mobile.bg access

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd mobilebg-carcrawler

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Edit the `.env` file to set your search criteria:

```bash
# Search Parameters
BRAND=mitsubishi         # Brand: mitsubishi, toyota, bmw, etc.
MODEL=outlander          # Model: outlander, camry, x5, etc.
VEHICLE_TYPE=dzhip       # Type: dzhip, sedan, kombi, hechbek, etc.
FUEL_TYPE=benzinov       # Fuel: benzinov, dizelov, gaz, elektricheski

# Price Range (Bulgarian Lev)
MIN_PRICE=5000
MAX_PRICE=12000

# Engine Power Range (Horsepower)
MIN_ENGINE_POWER=100
MAX_ENGINE_POWER=200

# Excel Export Settings
EXCEL_PATH=docs/car-data.xlsx
SHEET_NAME=Top-Picks
TABLE_NAME=TopPicks
```

### 4. Run the Crawler
```bash
# Start crawling with default settings
python crawler.py

# Or use interactive menu
python menu_crawler.py
```

## 🧪 Testing & Validation

The system includes comprehensive testing to ensure reliability:

### Quick Test Commands
```bash
# Run all tests (8 test suites)
.venv/bin/python Tests/run_all_tests.py

# Quick core functionality tests
.venv/bin/python Tests/test_quick.py core

# System health check
.venv/bin/python Tests/system_status.py --health
```

### Test Coverage
- ✅ **Price Extraction Tests**: EUR/BGN separation validation
- ✅ **Excel Export Tests**: File structure and data integrity
- ✅ **Pagination Tests**: Multi-page crawling verification
- ✅ **Production Date Tests**: Full Bulgarian date extraction
- ✅ **Complete System Tests**: End-to-end workflow validation
- ✅ **Excel Structure Tests**: 15-column optimization verification
- ✅ **Functionality Tests**: All components integration
- ✅ **Main Crawler Tests**: Real execution validation

## 📊 Data Output

### Excel Structure (15 Columns)
| Column | Type | Description |
|--------|------|-------------|
| Brand | Text | Car manufacturer |
| Model | Text | Car model name |
| Production Date | Text | Full date (e.g., "юни 2007") |
| Price_EUR | Numeric | Price in Euros |
| Price_BGN | Numeric | Price in Bulgarian Lev |
| Engine | Text | Engine specifications |
| Fuel Type | Text | Fuel type (benzinov, dizelov, etc.) |
| Transmission | Text | Transmission type |
| Mileage | Text | Odometer reading |
| Color | Text | Vehicle color |
| Location | Text | City/region |
| Phone | Text | Seller contact |
| Link | Text | Original listing URL |
| Описание | Text | Description in Bulgarian |
| Car Extras | Text | Additional features |

### Sample Console Output
```bash
🚀 NEW CRAWLER SESSION STARTED
================================================================================
🎮 Crawler Arguments: delay=0.5s, max_pages=100, excel=docs/car-data.xlsx
🔍 SEARCH CRITERIA:
📱 Vehicle: Mitsubishi Outlander (dzhip)
⛽ Fuel Type: benzinov
💰 Price Range: 5000 - 9000 BGN
🔧 Engine Power: 100 - 200 HP

📊 SEARCH RESULTS SUMMARY:
 🎯 Total Results Found: 38 cars
 📄 Estimated Pages: 2 pages (~20 cars per page)
 ⏱️  Estimated Crawl Time: ~1.0 seconds

📈 EXTRACTION COMPLETE!
  ✅ Successful Extractions: 38 cars
  ❌ Failed Extractions: 0 cars
  📊 Success Rate: 100.0%

💰 PRICE ANALYSIS:
  📊 Cars with Valid Prices: 38/38
  💵 Average Price: 7,068 BGN
  📉 Minimum Price: 5,000 BGN
  📈 Maximum Price: 8,999 BGN

🎯 MISSION COMPLETE! 🚀
```

## ⚙️ Command Line Options

```bash
# Basic usage
python crawler.py

# Custom options
python crawler.py --delay 0.5 --max-pages 5 --excel custom-cars.xlsx

# Available options
--delay SECONDS      # Delay between requests (default: 1.0)
--max-pages NUMBER   # Maximum pages to crawl (default: 100)
--excel PATH         # Excel output file path
--help              # Show all options
```

## 🎮 Interactive Menu

Use `menu_crawler.py` for a user-friendly interface with preset configurations:

1. **🏎️ Luxury German SUVs** - BMW X5 (20k-80k BGN, 200-500 HP)
2. **🚙 Reliable Japanese SUVs** - Honda CR-V (8k-25k BGN, 120-200 HP)
3. **💼 Executive Sedans** - Mercedes E-Class (15k-60k BGN, 150-400 HP)
4. **💰 Budget-Friendly Cars** - Toyota Corolla (3k-15k BGN, 90-150 HP)
5. **⚡ Electric Vehicles** - Tesla Model 3 (25k-100k BGN, 200-500 HP)
...and more!

## 🔧 Configuration Examples

### Luxury SUVs Search
```bash
BRAND=bmw
MODEL=x5
VEHICLE_TYPE=dzhip
MIN_PRICE=20000
MAX_PRICE=80000
MIN_ENGINE_POWER=200
MAX_ENGINE_POWER=500
```

### Budget Cars Search
```bash
BRAND=toyota
MODEL=corolla
VEHICLE_TYPE=sedan
MIN_PRICE=3000
MAX_PRICE=15000
MIN_ENGINE_POWER=90
MAX_ENGINE_POWER=150
```

### Electric Vehicles Search
```bash
BRAND=tesla
MODEL=model-3
FUEL_TYPE=elektricheski
MIN_PRICE=25000
MAX_PRICE=100000
```

## 📁 Project Structure

```
mobilebg-carcrawler/
├── 📄 crawler.py                    # Main crawler script
├── 📄 menu_crawler.py               # Interactive menu interface
├── 📄 .env                          # Main configuration
├── 📄 requirements.txt              # Dependencies
├── 📁 modules/                      # Core components
│   ├── config_manager.py            # Configuration handling
│   ├── extractors.py               # Data extraction logic
│   ├── web_scraper.py              # Multi-page crawling
│   ├── excel_utils.py              # Excel export with formatting
│   ├── url_builder.py              # Search URL construction
│   └── url_validator.py            # URL validation
├── 📁 Tests/                        # Comprehensive test suite
│   ├── run_all_tests.py            # Master test runner
│   ├── test_quick.py               # Quick test categories
│   ├── system_status.py            # System status and health
│   ├── test_production_date_extraction.py
│   ├── test_excel_structure.py
│   ├── test_complete_functionality.py
│   └── test_main_crawler_execution.py
├── 📁 presets/                      # Pre-configured searches
│   ├── .env.toyota-corolla
│   ├── .env.bmw-x5
│   └── ... (multiple presets)
├── 📁 docs/                         # Auto-created output
│   └── car-data.xlsx               # Excel exports
└── 📄 crawler.log                  # Detailed session logs
```

## 🛠️ Advanced Usage

### Performance Tuning
```bash
# Fast crawling (be respectful)
python crawler.py --delay 0.3

# Conservative crawling  
python crawler.py --delay 2.0

# Limited pages for testing
python crawler.py --max-pages 2
```

### Custom Presets
Create new search configurations in the `presets/` folder:

```bash
# Copy existing preset
cp presets/.env.toyota-corolla presets/.env.my-search

# Edit parameters
nano presets/.env.my-search

# Use with environment variable
ENV_FILE=presets/.env.my-search python crawler.py
```

## 🔍 Troubleshooting

### Common Issues

**❌ "Environment file not found"**
- Ensure you're in the project directory and `.env` exists

**❌ "URL returns 404"**
- Check brand/model combination exists on mobile.bg
- Verify Bulgarian spelling (e.g., `benzinov` not `benzin`)

**❌ "No results found"**
- Adjust price range or engine power limits
- Check if fuel type matches mobile.bg categories

**❌ "Module not found"**
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Debug Commands
```bash
# Check logs for detailed information
tail -f crawler.log

# Test with single page
python crawler.py --max-pages 1 --delay 0.1

# Run system health check
python Tests/system_status.py --health

# Verify test status
python Tests/run_all_tests.py
```

## 📈 System Performance

- **🎯 Success Rate**: 100% (all tests passing)
- **🕷️ Crawling Speed**: ~38 cars in 25 seconds
- **📈 Data Quality**: Full production dates + location detection
- **💰 Price Accuracy**: Separate EUR/BGN with proper numeric types
- **📁 Excel Output**: Auto-created with 15 optimized columns
- **🔄 Pagination**: All pages crawled (e.g., 38/38 cars collected)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run the test suite: `python Tests/run_all_tests.py`
4. Make your changes
5. Ensure all tests pass
6. Submit a pull request

## 📄 License & Disclaimer

This project is for educational and personal research purposes only. 

**Important Guidelines:**
- Respect mobile.bg's terms of service
- Use reasonable delays between requests (default 1.0s)
- Don't overload servers with excessive requests
- Personal use only - not for commercial data harvesting

## 🆘 Support

For issues or questions:
1. Check the `crawler.log` file for detailed error information
2. Run health check: `python Tests/system_status.py --health`
3. Review test results: `python Tests/run_all_tests.py`
4. Check this documentation for common solutions

---

**🚀 Happy Car Hunting!** 

*Built with ❤️ for the Bulgarian automotive market research community*