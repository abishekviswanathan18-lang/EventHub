from django.contrib import admin
from .models import Category, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'event_date', 'city', 'status']
    list_filter = ['status', 'category', 'city']
    search_fields = ['title', 'city']

# Register your models here.

from .models import Category, Event, EventImage


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ['event', 'uploaded_at']
