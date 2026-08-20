from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from events.models import Event
from bookings.models import Booking
from .models import Review
from .forms import ReviewForm


@login_required
def add_review_view(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    # Check 1: event must have already happened
    if event.event_date >= timezone.now().date():
        messages.error(request, "You can only review an event after it has taken place.")
        return redirect('event_detail', pk=event.pk)

    # Check 2: user must have a CONFIRMED booking for this event
    has_booking = Booking.objects.filter(
        user=request.user,
        event=event,
        status=Booking.Status.CONFIRMED
    ).exists()

    if not has_booking:
        messages.error(request, "You can only review events you've booked and attended.")
        return redirect('event_detail', pk=event.pk)

    # Check 3: no duplicate review
    existing_review = Review.objects.filter(event=event, user=request.user).first()
    if existing_review:
        messages.error(request, "You've already reviewed this event.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.event = event
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {'form': form, 'event': event})