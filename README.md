# 🚗 MobileBG CarCrawler

Web scraper for mobile.bg (Bulgarian car marketplace) that extracts car data and exports to Excel.

## ✨ Features

- **Multi-page crawling** - Gets ALL results, not just first 20
- **Excel export** - Separate EUR/BGN price columns + 15 data fields
- **Bulgarian date extraction** - Full production dates
- **Preset configurations** - Ready-to-use search templates

## 🚀 Quick Start

### 1. Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run
```bash
# Interactive menu with presets
python menu_crawler.py

# Or direct crawling
python crawler.py --max-pages 20 --delay 0.8
```

### 3. Configuration
Edit `.env` file or use presets from `presets/` folder:

```bash
BRAND=audi
MODEL=a4
VEHICLE_TYPE=sedan
FUEL_TYPE=dizelov
MIN_PRICE=8000
MAX_PRICE=35000
```

## 🧪 Testing

```bash
# Run all tests
python Tests/run_all_tests.py

# Quick health check
python Tests/system_status.py --health
```

## 📊 Output

**Excel file with 15 columns:**
Brand, Model, Production Date, Price_EUR, Price_BGN, Engine, Fuel Type, Transmission, Mileage, Color, Location, Phone, Link, Description, Extras

**Example results:**
```
🎯 Total Results Found: 140 cars
✅ Successful Extractions: 140/140 (100%)
💵 Average Price: 13,828 BGN
� Saved to: docs/audi-a4-complete.xlsx
```

## ⚙️ Options

```bash
# Basic usage
python crawler.py

# Get ALL results (not just first 20)
python crawler.py --max-pages 20 --delay 0.8

# Custom Excel output file
python crawler.py --excel my-cars.xlsx

# Fast crawling (be respectful to server)
python crawler.py --delay 0.3 --max-pages 10

# Conservative crawling with longer delays
python crawler.py --delay 2.0

# Test with limited pages
python crawler.py --max-pages 2 --delay 0.1

# All options combined
python crawler.py --max-pages 15 --delay 0.5 --excel custom-search.xlsx

# Use presets
cp presets/.env.audi-a4 .env
python crawler.py

# Available presets:
# .env.audi-a4, .env.bmw-x5, .env.tesla-model3, .env.toyota-corolla, etc.

# See all available options
python crawler.py --help
```

## 📁 Files

```
crawler.py           # Main script
menu_crawler.py      # Interactive menu
.env                 # Configuration
presets/             # Ready-to-use configs
Tests/               # Test suite
docs/                # Excel output
```

## � Troubleshooting

**Missing dependencies:** `pip install -r requirements.txt`  
**Only getting first 20 results:** Use `--max-pages 20`  
**Module errors:** Activate venv: `source .venv/bin/activate`  

## � Notes

- Respects mobile.bg with configurable delays
- For educational/research use only
- Check logs in `crawler.log` for detailed info