from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('crawl/', views.crawler_view, name='crawler'),
    path('crawl/start/', views.start_crawl, name='start_crawl'),
    path('crawl/status/<uuid:session_id>/', views.crawl_status, name='crawl_status'),
    path('crawl/logs/<uuid:session_id>/', views.crawl_logs, name='crawl_logs'),
    path('crawl/stop/<uuid:session_id>/', views.stop_crawl, name='stop_crawl'),
    
    path('results/', views.results_view, name='results'),
    path('results/delete/<int:listing_id>/', views.delete_listing, name='delete_listing'),
    path('results/export/<uuid:session_id>/', views.export_session_excel, name='export_session'),
    path('results/export-all/', views.export_all_excel, name='export_all'),
    
    path('presets/', views.presets_view, name='presets'),
    path('presets/create/', views.create_preset, name='create_preset'),
    path('presets/edit/<int:preset_id>/', views.edit_preset, name='edit_preset'),
    path('presets/delete/<int:preset_id>/', views.delete_preset, name='delete_preset'),
    
    path('health/', views.health_check, name='health_check'),
]
