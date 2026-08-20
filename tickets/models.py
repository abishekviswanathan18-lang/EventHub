from django.db import models
from events.models import Event


class TicketType(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='ticket_types'
    )
    name = models.CharField(max_length=100)  # e.g. "Regular", "VIP"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # When first created, available = total
        if self._state.adding:
            self.available_quantity = self.total_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event.title} - {self.name}"