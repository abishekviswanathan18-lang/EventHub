from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'booking_item', 'is_checked_in', 'checked_in_at']
    list_filter = ['is_checked_in']