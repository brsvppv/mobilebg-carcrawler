from django.db import models
import uuid

class SearchPreset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    filename = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=50, default='sedan')
    fuel_type = models.CharField(max_length=50, default='dizelov')
    min_price = models.IntegerField(default=5000)
    max_price = models.IntegerField(default=30000)
    min_power = models.IntegerField(default=100)
    max_power = models.IntegerField(default=300)
    max_pages = models.IntegerField(default=20)
    delay = models.FloatField(default=0.5)

    def __str__(self):
        return self.name


class CrawlSession(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('stopped', 'Stopped'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='running')
    search_description = models.CharField(max_length=255)
    total_found = models.IntegerField(null=True, blank=True)
    processed_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    fail_count = models.IntegerField(default=0)
    logs = models.TextField(blank=True, default='')
    excel_file_path = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.search_description} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"


class CarListing(models.Model):
    session = models.ForeignKey(CrawlSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    production_date = models.CharField(max_length=50, blank=True, null=True)
    price_eur = models.FloatField(null=True, blank=True)
    price_bgn = models.IntegerField(null=True, blank=True)
    engine = models.CharField(max_length=100, blank=True, null=True)
    fuel_type = models.CharField(max_length=50, blank=True, null=True)
    transmission = models.CharField(max_length=50, blank=True, null=True)
    mileage = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    link = models.URLField(max_length=500, unique=True)
    description = models.TextField(blank=True, null=True)
    extras = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} - {self.price_bgn or self.price_eur or 'N/A'}"
