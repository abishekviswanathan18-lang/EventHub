from django.contrib import admin
from .models import Booking, BookingItem


class BookingItemInline(admin.TabularInline):
    model = BookingItem
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'total_amount', 'status', 'booking_date']
    list_filter = ['status']
    inlines = [BookingItemInline]

# Register your models here.

from .models import Booking, BookingItem, Refund


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'status', 'requested_at', 'processed_at']
    list_filter = ['status']
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status=Refund.Status.PENDING).update(
            status=Refund.Status.PROCESSED,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} refund(s) marked as processed.')
    mark_as_processed.short_description = 'Mark selected refunds as processed'