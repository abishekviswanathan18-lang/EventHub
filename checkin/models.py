import uuid
from io import BytesIO
from django.db import models
from django.core.files import File
import qrcode
from bookings.models import BookingItem


class Ticket(models.Model):
    booking_item = models.ForeignKey(
        BookingItem,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    ticket_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr_img = qrcode.make(str(self.ticket_number))
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            filename = f'ticket_{self.ticket_number}.png'
            self.qr_code.save(filename, File(buffer), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.ticket_number} - {'Checked In' if self.is_checked_in else 'Valid'}"