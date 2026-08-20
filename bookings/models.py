from django.db import models
from django.conf import settings
from events.models import Event
from tickets.models import TicketType


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED
    )

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} - {self.event.title}"


class BookingItem(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='items'
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ticket_type.name} x{self.quantity}"


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSED = 'PROCESSED', 'Processed'

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='refund'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund for Booking #{self.booking.id} - {self.status}"