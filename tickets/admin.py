from django.contrib import admin
from .models import TicketType


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ['event', 'name', 'price', 'total_quantity', 'available_quantity']
    list_filter = ['event']