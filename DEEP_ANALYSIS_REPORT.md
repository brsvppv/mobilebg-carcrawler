# DEEP_ANALYSIS_REPORT.md

## 1. Inventory of Codebase

| File/Folder Path | Size (Bytes) | Primary Purpose / Role | Dependencies |
|---|---|---|---|
| `crawler.py` | ~6,684 | Main CLI entry point. Coordinate config loading, URL building, validation, links collection, details extraction, pricing analysis, and Excel exporting. | `modules/config_manager.py`, `modules/logger_config.py`, `modules/url_builder.py`, `modules/url_validator.py`, `modules/web_scraper.py`, `modules/extractors.py`, `modules/excel_utils.py` |
| `menu_crawler.py` | ~13,317 | Interactive CLI menu helper. Parses presets, configures crawl parameters, updates `.env`, and runs `crawler.py` as a subprocess. | `subprocess`, `os`, `sys`, `pathlib` |
| `manage.py` | ~685 | Django administrative command-line utility. | `django.core.management` |
| `web_app/settings.py` | ~4,200 | Django project configuration including SQLite database, middleware, templates, and static directories. | `django` |
| `web_app/urls.py` | ~800 | Main URL configuration and routing. | `django.urls`, `crawler_ui` |
| `crawler_ui/models.py` | ~3,493 | Database schema definition. Contains `SearchPreset`, `CrawlSession`, and `CarListing`. | `django.db` |
| `crawler_ui/views.py` | ~15,552 | View controllers for Dashboard, Crawl status panel, Results data tables, Presets CRUD. | `django.shortcuts`, `django.http`, `django.db.models`, `crawler_ui/models.py`, `crawler_ui/crawl_worker.py` |
| `crawler_ui/urls.py` | ~1,189 | Django routing for scraper views, HTMX partials, exports, and presets. | `django.urls`, `crawler_ui/views.py` |
| `crawler_ui/crawl_worker.py`| ~7,777 | Background threading wrapper to run scraper jobs asynchronously without celery. | `threading`, `time`, `logging`, `crawler_ui/models.py`, `modules/...` |
| `modules/config_manager.py`| ~1,644 | Interface for parsing `.env` file configurations. | `os`, `dotenv` |
| `modules/logger_config.py`| ~1,439 | Configures terminal stdout and file-based logging. | `logging` |
| `modules/url_builder.py` | ~2,300 | Generates search URLs for mobile.bg. | `os`, `logging` |
| `modules/url_validator.py` | ~2,257 | Validates search query URL returns list items and not error/empty pages. | `requests`, `bs4` |
| `modules/web_scraper.py` | ~7,392 | Pagination-based crawler traversing search pages to harvest unique listing links. | `requests`, `bs4` |
| `modules/extractors.py` | ~13,644 | Scrapes detailed car specifications, pricing, location, and description from a single listing page. | `requests`, `bs4`, `re` |
| `modules/excel_utils.py` | ~6,665 | Formats lists of dictionary car items and exports them to styled Excel sheets. | `openpyxl`, `modules/excel_table_utils.py` |
| `modules/excel_table_utils.py`| ~1,130 | Safely determines Excel worksheet boundaries. | `openpyxl` |
| `.env` | ~594 | Active search and environment settings. | None |
| `requirements.txt` | ~59 | System dependencies declarations. | `django`, `requests`, `beautifulsoup4`, `openpyxl`, `python-dotenv` |

---

## 2. Code Flow Diagrams

### Scraper Execution Path (Background Thread)
```
[User Clicks "Launch" or Preset Run]
                  │
                  ▼
      [views.py: start_crawl()]
                  │
                  ▼
 [crawl_worker.py: start_crawl_in_background()]
                  │
                  ▼
 [crawl_worker.py: run_crawl_session() (Thread)]
                  │
                  ├─► [url_builder.py: build_mobilebg_search_url()]
                  ├─► [url_validator.py: validate_search_url()]
                  │
                  ▼
        (If URL is Valid)
                  │
                  ▼
    [web_scraper.py: get_all_listing_links()]
                  │
                  ▼
    (Loop: For Each Link Gathered)
                  │
                  ├─► [extractors.py: extract_car_info_unified()]
                  ├─► [crawl_worker.py: CarListing.objects.update_or_create()]
                  ├─► [crawl_worker.py: Update Progress & Logs in CrawlSession]
                  │
                  ▼
   [excel_utils.py: export_to_excel() (Saves XLS)]
                  │
                  ▼
       [Update Status to 'completed']
```

---

## 3. Dependency Graph

### Internal Modules & System Packages
```
                   ┌──────────────────┐
                   │  menu_crawler.py │
                   └────────┬─────────┘
                            │ (subprocess)
                            ▼
                   ┌──────────────────┐
                   │    crawler.py    │
                   └────────┬─────────┘
                            │
      ┌─────────────────────┼─────────────────────┐
      ▼                     ▼                     ▼
┌───────────┐         ┌───────────┐         ┌───────────┐
│url_builder│         │web_scraper│         │extractors │
└─────┬─────┘         └─────┬─────┘         └─────┬─────┘
      │                     │                     │
      └──────────────┬──────┴─────────────────────┘
                     ▼
             ┌──────────────┐
             │requests / bs4│
             └──────────────┘
```

---

## 4. List of Identified Issues & Bugs

| Category | Severity | Type | Description | Root Cause / Risk |
|---|---|---|---|---|
| **Calculated Price Parsing** | Critical | Logic | When listings have EUR prices, the BGN equivalent value stored was incorrectly truncated to only the decimal stotinki. | The parsing regex stripped spaces and didn't match the dot, stopping prematurely (e.g. `38136.73` matched only `73`). (Fixed) |
| **Preset Model Slugs** | High | Logic | BMW 3 Series preset targeted `seria-3` which returns 404 on mobile.bg, breaking the crawl session immediately. | Mobile.bg does not support grouped series paths; specific numeric models (e.g. `320`) must be used. (Fixed) |
| **Filters Dropdown UI** | High | UX / Logic | The search filters dropdown options for Fuel Type and Transmission were hardcoded and did not align with actual database fields, rendering filtering useless. | Hardcoded HTML string values (e.g., `dizel`, `benzin`) did not match scraped Cyrillic strings (e.g. `Дизелов`, `Бензинов`). (Fixed) |
| **Sequential Requests Bottleneck** | Medium | Performance | Crawling is entirely sequential and synchronous, meaning extracting 200+ car listings with a 0.5s delay takes several minutes. | Single-threaded synchronous network IO blocking execution. |
| **DB Locking Risk** | Medium | Stability | Running multi-threaded database updates in SQLite without connection limits can lead to `database is locked` errors during heavy crawls. | SQLite does not support highly concurrent writes; simultaneous crawls can block each other. |
| **Lack of Scraper Proxy/User-Agent rotation** | Low | Security | The scraper uses a single hardcoded User-Agent and no proxy rotation, exposing it to easy IP blocks. | Mobile.bg rate-limiting or blocking could shut down scraper functionality completely. |

---

## 5. Performance Metrics (Estimates)

- **Search Page Load**: ~500ms per page via `requests`
- **Details Page Extract**: ~400ms - 800ms per listing
- **DB Write Overhead**: ~10ms per listing (SQLite write transaction)
- **Estimated Session Execution Time (100 cars, 0.5s delay)**: ~120 - 150 seconds.
- **Memory Footprint**: ~45MB - 60MB RAM usage during background thread extraction.

---

## 6. Stability Risks

1. **HTML Structure Changes**: Scraper depends heavily on specific BeautifulSoup queries (e.g., `soup.find('div', class_='Price')`). If mobile.bg updates their classes, the scraper will fail.
2. **Missing Rate Limit Handling**: If mobile.bg returns HTTP 429 (Too Many Requests), the scraper treats it as a non-200 code and aborts the crawl, rather than backing off or retrying with longer delay.
3. **SQLite Concurrent Write Collisions**: While background crawling works in a separate thread, launching multiple crawls concurrently will trigger SQLite database lock issues.

---
