import os
import math
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, Min, Max, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import SearchPreset, CrawlSession, CarListing
from .crawl_worker import start_crawl_in_background, ACTIVE_CRAWLS
from modules import excel_utils

def init_presets_if_empty():
    """Reads .env files in presets/ and populates SearchPreset DB table if it's empty."""
    if SearchPreset.objects.exists():
        return
        
    presets_dir = Path(__file__).parent.parent / 'presets'
    if not presets_dir.exists():
        return
        
    preset_paths = list(presets_dir.glob('.env.*'))
    for path in preset_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            info = {}
            for line in content.split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    info[key.strip()] = value.strip()
            
            brand = info.get('BRAND', 'generic')
            model = info.get('MODEL', 'car')
            preset_name = path.name.replace('.env.', '').replace('-', ' ').title()
            
            SearchPreset.objects.create(
                name=preset_name,
                filename=path.name,
                brand=brand,
                model=model,
                vehicle_type=info.get('VEHICLE_TYPE', 'sedan'),
                fuel_type=info.get('FUEL_TYPE', 'dizelov'),
                min_price=int(info.get('MIN_PRICE', 5000)),
                max_price=int(info.get('MAX_PRICE', 30000)),
                min_power=int(info.get('MIN_ENGINE_POWER', 100)),
                max_power=int(info.get('MAX_ENGINE_POWER', 300)),
                max_pages=int(info.get('MAX_PAGES', 20)),
                delay=float(info.get('DELAY', 0.5)),
            )
        except Exception:
            pass # Keep initializing others if one fails


def dashboard_view(request):
    init_presets_if_empty()
    
    # Core stats
    total_listings = CarListing.objects.count()
    total_sessions = CrawlSession.objects.count()
    avg_price_eur = CarListing.objects.filter(price_eur__isnull=False).aggregate(Avg('price_eur'))['price_eur__avg'] or 0
    
    # Top brands
    top_brands = CarListing.objects.values('brand').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Locations distribution
    location_data = CarListing.objects.values('location').annotate(count=Count('id')).filter(location__isnull=False).exclude(location='').order_by('-count')[:8]
    
    # Recent sessions
    recent_sessions = CrawlSession.objects.order_by('-start_time')[:5]
    
    context = {
        'total_listings': total_listings,
        'total_sessions': total_sessions,
        'avg_price_eur': round(avg_price_eur),
        'top_brands': top_brands,
        'location_data': location_data,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'crawler_ui/dashboard.html', context)


def crawler_view(request):
    init_presets_if_empty()
    presets = SearchPreset.objects.all()
    sessions = CrawlSession.objects.order_by('-start_time')[:10]
    
    # Check if we should automatically run a preset
    run_preset_id = request.GET.get('run_preset')
    running_session = CrawlSession.objects.filter(status='running').first()
    
    if run_preset_id:
        if not running_session:
            try:
                preset = SearchPreset.objects.get(id=run_preset_id)
                # Create session and trigger crawl
                running_session = CrawlSession.objects.create(
                    status='running',
                    search_description=f"Preset: {preset.name}"
                )
                start_crawl_in_background(
                    running_session.id, preset.brand, preset.model, preset.vehicle_type, preset.fuel_type,
                    preset.min_price, preset.max_price, preset.min_power, preset.max_power, preset.max_pages, preset.delay
                )
                # Re-fetch sessions list to include the newly started session
                sessions = CrawlSession.objects.order_by('-start_time')[:10]
            except SearchPreset.DoesNotExist:
                pass
        else:
            messages.warning(request, "A crawling session is already running! Please wait for it to finish or stop it first.")
            
    context = {
        'presets': presets,
        'sessions': sessions,
        'running_session': running_session,
    }
    return render(request, 'crawler_ui/crawler.html', context)


@require_POST
def start_crawl(request):
    # Check if a crawl is already running
    if CrawlSession.objects.filter(status='running').exists():
        return HttpResponse('<div class="alert alert-error">A crawling session is already running!</div>', status=400)
        
    preset_id = request.POST.get('preset_id')
    if preset_id:
        preset = get_object_or_404(SearchPreset, id=preset_id)
        brand = preset.brand
        model = preset.model
        vehicle_type = preset.vehicle_type
        fuel_type = preset.fuel_type
        min_price = preset.min_price
        max_price = preset.max_price
        min_power = preset.min_power
        max_power = preset.max_power
        max_pages = preset.max_pages
        delay = preset.delay
        desc = f"Preset: {preset.name}"
    else:
        brand = request.POST.get('brand', '').strip().lower()
        model = request.POST.get('model', '').strip().lower()
        vehicle_type = request.POST.get('vehicle_type', 'sedan').strip().lower()
        fuel_type = request.POST.get('fuel_type', 'dizelov').strip().lower()
        min_price = int(request.POST.get('min_price', 5000))
        max_price = int(request.POST.get('max_price', 30000))
        min_power = int(request.POST.get('min_power', 100))
        max_power = int(request.POST.get('max_power', 300))
        max_pages = int(request.POST.get('max_pages', 20))
        delay = float(request.POST.get('delay', 0.5))
        desc = f"Custom: {brand.title()} {model.title()}"

    if not brand or not model:
        return HttpResponse('<div class="alert alert-error">Brand and Model are required!</div>', status=400)

    # Create session
    session = CrawlSession.objects.create(
        status='running',
        search_description=desc
    )

    # Trigger async thread
    start_crawl_in_background(
        session.id, brand, model, vehicle_type, fuel_type,
        min_price, max_price, min_power, max_power, max_pages, delay
    )

    # Return the progress section template (which will start polling)
    return render(request, 'crawler_ui/partials/crawl_progress.html', {'session': session})


def crawl_status(request, session_id):
    session = get_object_or_404(CrawlSession, id=session_id)
    progress = 0
    if session.total_found and session.total_found > 0:
        progress = int((session.processed_count / session.total_found) * 100)
        
    context = {
        'session': session,
        'progress': progress,
    }
    return render(request, 'crawler_ui/partials/crawl_progress.html', context)


def crawl_logs(request, session_id):
    session = get_object_or_404(CrawlSession, id=session_id)
    return HttpResponse(session.logs or 'Initializing crawler...', content_type='text/plain')


@require_POST
def stop_crawl(request, session_id):
    session = get_object_or_404(CrawlSession, id=session_id)
    if session.status == 'running':
        session.status = 'stopped'
        session.end_time = timezone.now()
        session.save(update_fields=['status', 'end_time'])
    
    # For HTMX requests, use HX-Redirect to trigger a full page reload
    # instead of injecting redirect response into the target div
    if request.headers.get('HX-Request'):
        response = HttpResponse(status=200)
        response['HX-Redirect'] = request.build_absolute_uri('/crawl/')
        return response
    return redirect('crawler')


def results_view(request):
    query = request.GET.get('q', '')
    brand = request.GET.get('brand', '')
    fuel_type = request.GET.get('fuel_type', '')
    transmission = request.GET.get('transmission', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    session_id = request.GET.get('session', '')
    
    listings = CarListing.objects.all().order_by('-created_at')
    
    if session_id:
        listings = listings.filter(session_id=session_id)
    if query:
        listings = listings.filter(Q(brand__icontains=query) | Q(model__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
    if brand:
        listings = listings.filter(brand__iexact=brand)
    if fuel_type:
        listings = listings.filter(fuel_type=fuel_type)
    if transmission:
        listings = listings.filter(transmission=transmission)
    if min_price:
        listings = listings.filter(price_eur__gte=min_price)
    if max_price:
        listings = listings.filter(price_eur__lte=max_price)
        
    # Get distinct brands, fuels, transmissions for filtering options dynamically
    all_brands = CarListing.objects.filter(brand__isnull=False).exclude(brand='').values_list('brand', flat=True).distinct().order_by('brand')
    all_fuels = CarListing.objects.filter(fuel_type__isnull=False).exclude(fuel_type='').values_list('fuel_type', flat=True).distinct().order_by('fuel_type')
    all_transmissions = CarListing.objects.filter(transmission__isnull=False).exclude(transmission='').values_list('transmission', flat=True).distinct().order_by('transmission')
    
    paginator = Paginator(listings, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'all_brands': all_brands,
        'all_fuels': all_fuels,
        'all_transmissions': all_transmissions,
        'query': query,
        'brand': brand,
        'fuel_type': fuel_type,
        'transmission': transmission,
        'min_price': min_price,
        'max_price': max_price,
        'session_id': session_id,
    }
    
    # If HTMX request, render only the table body and pagination
    if request.headers.get('HX-Request'):
        return render(request, 'crawler_ui/partials/results_table.html', context)
        
    return render(request, 'crawler_ui/results.html', context)


@require_POST
def delete_listing(request, listing_id):
    listing = get_object_or_404(CarListing, id=listing_id)
    listing.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse('') # Empty response tells HTMX to remove the row from DOM
    return redirect('results')


def export_session_excel(request, session_id):
    # Ensure session_id is a UUID object (or handle string conversions)
    from uuid import UUID
    if isinstance(session_id, str):
        try:
            session_id = UUID(session_id)
        except ValueError:
            pass
            
    session = get_object_or_404(CrawlSession, id=session_id)
    
    # Construct a descriptive user-facing download filename based on search description
    clean_desc = "".join(c for c in session.search_description if c.isalnum() or c in (' ', '-', '_')).strip()
    clean_desc = clean_desc.replace(' ', '_').replace('-', '_').lower()
    download_filename = f"export_{clean_desc}_{session_id.hex[:6]}.xlsx" if clean_desc else f"export_{session_id.hex[:6]}.xlsx"
    
    if session.excel_file_path and os.path.exists(session.excel_file_path):
        response = FileResponse(open(session.excel_file_path, 'rb'), as_attachment=True, filename=download_filename)
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        return response
    else:
        # Generate on the fly
        listings = session.listings.all()
        if not listings:
            return HttpResponse("No listings to export", status=400)
            
        cars_data = []
        for car in listings:
            cars_data.append({
                'Brand': car.brand,
                'Model': car.model,
                'Production Date': car.production_date,
                'Price_EUR': car.price_eur or '',
                'Engine': car.engine or '',
                'Fuel Type': car.fuel_type or '',
                'Transmission': car.transmission or '',
                'Mileage': car.mileage or '',
                'Color': car.color or '',
                'Location': car.location or '',
                'Phone': car.phone or '',
                'Link': car.link,
                'Описание': car.description or '',
                'Car Extras': car.extras or ''
            })
            
        filename = f"docs/export-{session_id.hex[:6]}.xlsx"
        os.makedirs("docs", exist_ok=True)
        excel_utils.export_to_excel(cars_data, filename, "Scraped-Cars")
        session.excel_file_path = filename
        session.save(update_fields=['excel_file_path'])
        
        response = FileResponse(open(filename, 'rb'), as_attachment=True, filename=download_filename)
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        return response
 
 
def export_all_excel(request):
    listings = CarListing.objects.all()
    if not listings:
        return HttpResponse("No listings to export", status=400)
        
    cars_data = []
    for car in listings:
        cars_data.append({
            'Brand': car.brand,
            'Model': car.model,
            'Production Date': car.production_date,
            'Price_EUR': car.price_eur or '',
            'Engine': car.engine or '',
            'Fuel Type': car.fuel_type or '',
            'Transmission': car.transmission or '',
            'Mileage': car.mileage or '',
            'Color': car.color or '',
            'Location': car.location or '',
            'Phone': car.phone or '',
            'Link': car.link,
            'Описание': car.description or '',
            'Car Extras': car.extras or ''
        })
        
    filename = f"docs/all-cars-export.xlsx"
    os.makedirs("docs", exist_ok=True)
    excel_utils.export_to_excel(cars_data, filename, "All-Scraped-Cars")
    
    download_filename = "all_cars_export.xlsx"
    response = FileResponse(open(filename, 'rb'), as_attachment=True, filename=download_filename)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
    return response


def presets_view(request):
    init_presets_if_empty()
    presets = SearchPreset.objects.all()
    return render(request, 'crawler_ui/presets.html', {'presets': presets})


def create_preset(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        vehicle_type = request.POST.get('vehicle_type', 'sedan')
        fuel_type = request.POST.get('fuel_type', 'dizelov')
        min_price = request.POST.get('min_price', 5000)
        max_price = request.POST.get('max_price', 30000)
        min_power = request.POST.get('min_power', 100)
        max_power = request.POST.get('max_power', 300)
        max_pages = request.POST.get('max_pages', 20)
        delay = request.POST.get('delay', 0.5)
        
        SearchPreset.objects.create(
            name=name,
            brand=brand.strip().lower(),
            model=model.strip().lower(),
            vehicle_type=vehicle_type,
            fuel_type=fuel_type,
            min_price=int(min_price),
            max_price=int(max_price),
            min_power=int(min_power),
            max_power=int(max_power),
            max_pages=int(max_pages),
            delay=float(delay)
        )
        return redirect('presets')
        
    return render(request, 'crawler_ui/preset_form.html')


def edit_preset(request, preset_id):
    preset = get_object_or_404(SearchPreset, id=preset_id)
    if request.method == 'POST':
        preset.name = request.POST.get('name')
        preset.brand = request.POST.get('brand').strip().lower()
        preset.model = request.POST.get('model').strip().lower()
        preset.vehicle_type = request.POST.get('vehicle_type')
        preset.fuel_type = request.POST.get('fuel_type')
        preset.min_price = int(request.POST.get('min_price'))
        preset.max_price = int(request.POST.get('max_price'))
        preset.min_power = int(request.POST.get('min_power'))
        preset.max_power = int(request.POST.get('max_power'))
        preset.max_pages = int(request.POST.get('max_pages'))
        preset.delay = float(request.POST.get('delay'))
        preset.save()
        return redirect('presets')
        
    return render(request, 'crawler_ui/preset_form.html', {'preset': preset})


@require_POST
def delete_preset(request, preset_id):
    preset = get_object_or_404(SearchPreset, id=preset_id)
    preset.delete()
    return redirect('presets')


def health_check(request):
    """Simple health check endpoint for monitoring."""
    try:
        # Verify DB connectivity
        listing_count = CarListing.objects.count()
        session_count = CrawlSession.objects.count()
        running_crawls = CrawlSession.objects.filter(status='running').count()
        
        return JsonResponse({
            'status': 'healthy',
            'db': 'connected',
            'listings': listing_count,
            'sessions': session_count,
            'running_crawls': running_crawls,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
        }, status=503)

