from django.db.models import Sum, Count, Avg

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Category, EventImage
from .forms import EventForm, EventImageForm


from django.core.paginator import Paginator


def event_list_view(request):
    events = Event.objects.filter(status=Event.Status.PUBLISHED).order_by('event_date')

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    city = request.GET.get('city')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if query:
        events = events.filter(title__icontains=query)
    if category_id:
        events = events.filter(category_id=category_id)
    if city:
        events = events.filter(city=city)
    if date_from:
        events = events.filter(event_date__gte=date_from)
    if date_to:
        events = events.filter(event_date__lte=date_to)
    if min_price:
        events = events.filter(ticket_types__price__gte=min_price)
    if max_price:
        events = events.filter(ticket_types__price__lte=max_price)

    events = events.distinct()

    categories = Category.objects.all()
    cities = Event.objects.filter(
        status=Event.Status.PUBLISHED
    ).values_list('city', flat=True).distinct().order_by('city')

    paginator = Paginator(events, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'cities': cities,
    })


def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    reviews = event.reviews.all()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    user_has_reviewed = False
    is_favorited = False
    if request.user.is_authenticated:
        user_has_reviewed = reviews.filter(user=request.user).exists()
        is_favorited = event.favorited_by.filter(user=request.user).exists()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_has_reviewed': user_has_reviewed,
        'is_favorited': is_favorited,
    })

@login_required
def event_create_view(request):
    if request.user.role != 'ORGANIZER':
        messages.error(request, 'Only organizers can create events.')
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form})

# Create your views here.


from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from bookings.models import BookingItem


@login_required
def organizer_dashboard_view(request):
    if request.user.role != 'ORGANIZER':
        messages.error(request, 'Only organizers can access the dashboard.')
        return redirect('home')

    events = Event.objects.filter(organizer=request.user).order_by('-event_date')

    total_events = events.count()

    booking_items = BookingItem.objects.filter(
        ticket_type__event__organizer=request.user,
        booking__status='CONFIRMED'
    )

    total_tickets_sold = booking_items.aggregate(total=Sum('quantity'))['total'] or 0
    total_revenue = booking_items.aggregate(total=Sum('subtotal'))['total'] or 0

    # Per-event breakdown
    events_data = []
    for event in events:
        sold = BookingItem.objects.filter(
            ticket_type__event=event,
            booking__status='CONFIRMED'
        ).aggregate(total=Sum('quantity'))['total'] or 0

        total_capacity = event.ticket_types.aggregate(total=Sum('total_quantity'))['total'] or 0

        events_data.append({
            'event': event,
            'sold': sold,
            'capacity': total_capacity,
        })

    return render(request, 'events/organizer_dashboard.html', {
        'total_events': total_events,
        'total_tickets_sold': total_tickets_sold,
        'total_revenue': total_revenue,
        'events_data': events_data,
    })

@login_required
def event_edit_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.organizer != request.user:
        messages.error(request, 'You can only edit your own events.')
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'editing': True, 'event': event})


@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.organizer != request.user:
        messages.error(request, 'You can only delete your own events.')
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('organizer_dashboard')

    return render(request, 'events/event_confirm_delete.html', {'event': event})



@login_required
def add_event_image_view(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if event.organizer != request.user:
        messages.error(request, 'You can only add photos to your own events.')
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = EventImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.event = event
            image.save()
            messages.success(request, 'Photo added!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventImageForm()

    return render(request, 'events/event_image_form.html', {'form': form, 'event': event})


@login_required
def delete_event_image_view(request, image_pk):
    image = get_object_or_404(EventImage, pk=image_pk)

    if image.event.organizer != request.user:
        messages.error(request, 'You can only delete photos from your own events.')
        return redirect('event_detail', pk=image.event.pk)

    if request.method == 'POST':
        event_pk = image.event.pk
        image.delete()
        messages.success(request, 'Photo removed.')
        return redirect('event_detail', pk=event_pk)

    return redirect('event_detail', pk=image.event.pk)

from django.http import JsonResponse


def event_search_suggestions_view(request):
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    events = Event.objects.filter(
        status=Event.Status.PUBLISHED,
        title__icontains=query
    ).values('id', 'title', 'city')[:6]

    return JsonResponse({'results': list(events)})