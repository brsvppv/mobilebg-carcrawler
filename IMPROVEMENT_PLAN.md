# IMPROVEMENT_PLAN.md

## 1. Applied Bug Fixes

### A. Calculated Price Parsing Fix
- **Root Cause**: EUR prices translated to BGN with decimals (e.g., `38 136.73 лв.`) had spaces stripped, turning them into `38136.73лв.`. The regex `([\d\s]+)\s*лв` matched only `73` because the `[\d\s]+` token stops at the decimal dot.
- **Solution**: Updated the extraction regex in [extractors.py](file:///c:/GitHub/mobilebg-carcrawler/modules/extractors.py) to match digits and dots (`[\d\.]+`) and parse them as floats before rounding to the nearest integer.
- **Code Snippet**:
```python
# Look for BGN price (format: "5 799 лв." or containing decimal: "38 136.73 лв.")
bgn_match = re.search(r'([\d\.]+)\s*лв', price_text.replace(' ', ''))
if bgn_match:
    bgn_price = bgn_match.group(1)
    try:
        car_info['Price_BGN'] = int(round(float(bgn_price)))
    except ValueError:
        car_info['Price_BGN'] = ''
```

### B. BMW 3 Series Preset Correction
- **Root Cause**: The model preset configured `MODEL=seria-3`, which is not a recognized path on mobile.bg, resulting in a 404 URL.
- **Solution**: Changed the model target to `320` in [presets/.env.bmw-3series](file:///c:/GitHub/mobilebg-carcrawler/presets/.env.bmw-3series) and updated the SQLite database configurations.

### C. Dynamic Dropdown Filters
- **Root Cause**: The Fuel Type and Transmission filter options were hardcoded (e.g., `dizel` or `автоматик`) which did not match Cyrillic database values (e.g. `Дизелов` or `Автоматична`).
- **Solution**: Updated [views.py](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/views.py) to fetch unique values dynamically from the database and populate the options in [results.html](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/templates/crawler_ui/results.html).

---

## 2. Proposing Performance Improvements

### A. Database Indexing
- **Action**: Ensure database indices exist for frequently queried and filtered fields.
- **Details**: Django models in [models.py](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/models.py) have already been set up with indexes:
  - `idx_listing_created` on `created_at` (for ordering)
  - `idx_listing_brand_price` on `brand` and `price_bgn` (for fast filtering)
  - `idx_session_status` and `idx_session_start` on `CrawlSession` (for dashboard metrics)

### B. Async Requests / Multithreading Scraper
- **Action**: Add concurrent details extraction using a thread pool.
- **Example Code (Alternative to Sequential Crawling)**:
```python
from concurrent.futures import ThreadPoolExecutor

def extract_all_listings_concurrently(links, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(extract_car_info_unified, links)
    return [r for r in results if r]
```
> [!NOTE]
> Care must be taken not to trigger defensive rate-limiting (WAF) blocks on mobile.bg when executing concurrent HTTP calls.

---

## 3. Proposing Stability Improvements

### A. SQLite Connection Timeout / WAL Mode
- **Action**: Set write-ahead logging (WAL) and increase database busy timeout to prevent `database is locked` issues.
- **Configuration (in settings.py)**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Increase timeout to 20 seconds
        }
    }
}
```
And enable WAL mode on startup:
```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('PRAGMA journal_mode=WAL;')
```

### B. Defensive Web Scraping (Rate Limit Backoff)
- **Action**: Implement exponential backoff when requests encounter HTTP 429 status.
- **Example Code**:
```python
import time
# Inside request block
for attempt in range(retries):
    response = requests.get(url, headers=headers, timeout=timeout)
    if response.status_code == 429:
        time.sleep(2 ** attempt)  # Back off
        continue
    ...
```

---

## 4. Visual & UI Improvement Design

### Current UI Stack
- **Backend**: Django 4.x
- **Frontend**: HTMX (for dynamic state updates without page refreshes)
- **CSS System**: Premium Glassmorphism styling with modern CSS variables.

### Complete File Tree of Web App Components:
```
c:/GitHub/mobilebg-carcrawler/
├── web_app/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── crawler_ui/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── crawl_worker.py
    ├── templates/
    │   └── crawler_ui/
    │       ├── base.html
    │       ├── crawler.html
    │       ├── dashboard.html
    │       ├── presets.html
    │       ├── results.html
    │       └── partials/
    │           ├── crawl_progress.html
    │           └── results_table.html
    └── static/
        └── css/
            └── style.css
```

### Mockup / Design Decisions:
- **Global Theme**: Dark-mode primary palette (`#0f172a` slate background, glassmorphism border card effects with semi-transparent backings).
- **Navigation Bar**: Flat top navbar displaying current database health status and session counts.
- **Responsive Tables**: Car data tables with layout adjustments (`overflow-x: auto`) for mobile screens and quick deletion buttons powered by HTMX (`hx-post` + `hx-target="closest tr"`).
