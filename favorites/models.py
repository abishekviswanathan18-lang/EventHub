from django.db import models
from django.conf import settings
from events.models import Event


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')  # can't favorite the same event twice

    def __str__(self):
        return f"{self.user.username} ♥ {self.event.title}"