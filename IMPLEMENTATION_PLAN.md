# IMPLEMENTATION_PLAN.md

## 1. Goal Description
The goal is to convert the existing CLI mobile.bg scraper into a full-stack Django web application with a modern dashboard UI. The UI will use HTMX for real-time progress updates, page interactions, and asynchronous operations (like running crawlers). Styling will be managed using custom, premium-looking modern CSS. SQLite will act as the database, storing crawl sessions, scraped car details, and presets.

---

## 2. Assumptions
* The crawler can be executed locally in a separate thread/process inside the Django server without requiring heavy brokers like Celery/Redis.
* The database will keep track of crawled runs, listing links, and car details to allow persistence and analytics.
* Port 8000 is available for the local web server.

---

## 3. Proposed Changes

### Dependencies
Update [requirements.txt](file:///c:/GitHub/mobilebg-carcrawler/requirements.txt) to include Django.

### Django Project Structure
Initialize a Django project `web_app` and a Django app `crawler_ui` within the repository root.

#### [NEW] [manage.py](file:///c:/GitHub/mobilebg-carcrawler/manage.py)
Standard Django project entrypoint located in the repository root.

#### [NEW] [settings.py](file:///c:/GitHub/mobilebg-carcrawler/web_app/settings.py)
Django configuration file. Includes database setups (SQLite), registration of `crawler_ui`, and static/templates directory configurations.

#### [NEW] [urls.py](file:///c:/GitHub/mobilebg-carcrawler/web_app/urls.py)
Main routing file directing requests to `crawler_ui.urls`.

#### [NEW] [models.py](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/models.py)
Defines models:
* `CrawlSession`: Tracks status (running, completed, failed), brand/model crawled, total found, progress, and logs.
* `CarListing`: Stores individual car details (brand, model, price_eur, price_bgn, transmission, fuel, mileage, phone, location, extras, description, link).
* `SearchPreset`: Stores search configurations (brand, model, price range, etc.), syncing with the `presets/` directory.

#### [NEW] [views.py](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/views.py)
Contains views for:
* **Dashboard**: Statistics (scrapes, averages, locations chart, recent sessions).
* **Crawl Interface**: Configuration forms, triggering async crawling threads, and progress/log streams.
* **Results Table**: Searchable, filterable list of all crawled listings, with delete options and Excel generation triggers.
* **Presets Manager**: CRUD for presets, allowing saving presets back to the `presets/` folder or DB.

#### [NEW] [urls.py](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/urls.py)
Define sub-routing paths including HTMX partials.

#### [NEW] [templates](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/templates/)
HTML files utilizing Jinja2-like Django syntax:
* `base.html`: Common layout with dashboard navigation, global styles, and HTMX scripting.
* `dashboard.html`: Statistics panels, charts (using SVG/CSS or minimal canvas), and recent crawl cards.
* `crawler.html`: Crawl controls, custom crawler form, preset selector, and HTMX active progress container.
* `results.html`: Search filter form and table view of car listings.
* `presets.html`: Grid of existing presets with option to run, edit, or delete them.

#### [NEW] [static](file:///c:/GitHub/mobilebg-carcrawler/crawler_ui/static/)
* `css/style.css`: Modern styling sheet using variables, CSS Grid, cards, rounded corners, subtle shadows, hover effects, dark-mode inspired color schemes, and micro-animations.
* `js/main.js`: Micro-behaviors (e.g. confirmation prompts, quick charts).

---

## 4. Step-by-Step Tasks

| Task | Description | Effort | Files |
| --- | --- | --- | --- |
| **1. Install Deps** | Add Django to `requirements.txt` and install dependencies. | Low | `requirements.txt` |
| **2. Init Django** | Set up `manage.py`, `settings.py`, `urls.py`, and database migrations. | Low | New `web_app/` and `crawler_ui/` directories |
| **3. Models** | Define `CrawlSession`, `CarListing`, `SearchPreset` models. Run migrations. | Medium | `crawler_ui/models.py` |
| **4. Scraper Hook** | Adapt scraper logic (`crawler.py` / `extractors.py`) to write results to Django Models. | Medium | `crawler_ui/crawl_worker.py` |
| **5. Templates & CSS**| Create base layout and design system (CSS styling, responsive grid). | Medium | Templates & static CSS/JS |
| **6. Views & HTMX** | Implement dashboard analytics, asynchronous crawl runner (HTMX progress polling), results view, and presets management. | High | `views.py`, templates, URLs |
| **7. Verification** | Run server, test crawl sessions, verify Excel exports, inspect UI functionality. | Low | Manual / system testing |

---

## 5. Testing & Verification Plan
### Automated Verification
* Run Django test suite to verify database CRUD operations.
* Verify model constraints and export functionality.

### Manual Verification
* Access the web interface on `http://127.0.0.1:8000/`.
* Configure and launch a crawl using a preset. Verify the progress updates dynamically and logs appear.
* View crawled results in the list, test filters/search, and test "Export to Excel" download.

---

## 6. Rollback Plan
To revert, checkout the original branch (`main`), delete the newly created `web_app`, `crawler_ui`, and `manage.py` files, and run `pip install -r requirements.txt` to restore the virtual environment.
