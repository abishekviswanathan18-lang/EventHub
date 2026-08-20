from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from events.models import Event


class Review(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')  # one review per user per event
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.rating}★)"