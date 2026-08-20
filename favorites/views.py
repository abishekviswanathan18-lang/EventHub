from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from events.models import Event
from .models import Favorite


@login_required
def toggle_favorite_view(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if request.method == 'POST':
        favorite = Favorite.objects.filter(user=request.user, event=event).first()

        if favorite:
            favorite.delete()
            messages.success(request, 'Removed from favorites.')
        else:
            Favorite.objects.create(user=request.user, event=event)
            messages.success(request, 'Added to favorites!')

    return redirect('event_detail', pk=event.pk)


@login_required
def my_favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('event').order_by('-created_at')
    return render(request, 'favorites/my_favorites.html', {'favorites': favorites})