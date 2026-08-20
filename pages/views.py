from django.shortcuts import render, redirect
from django.contrib import messages
from events.models import Event, Category
from events.recommendations import get_recommended_events

CATEGORY_ICONS = {
    'Music': '🎵',
    'Technology': '💻',
    'Sports': '⚽',
    'Workshop': '🛠️',
    'Business': '💼',
    'Education': '📚',
}


def home_view(request):
    featured_events = Event.objects.filter(
        status=Event.Status.PUBLISHED
    ).order_by('event_date')[:4]

    categories = Category.objects.all()
    for cat in categories:
        cat.icon = CATEGORY_ICONS.get(cat.name, '🎟️')

    recommended_events = get_recommended_events(request.user)

    total_events_count = Event.objects.filter(status=Event.Status.PUBLISHED).count()
    total_cities_count = Event.objects.filter(
        status=Event.Status.PUBLISHED
    ).values_list('city', flat=True).distinct().count()

    from bookings.models import BookingItem
    from django.db.models import Sum
    total_tickets_count = BookingItem.objects.filter(
        booking__status='CONFIRMED'
    ).aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'pages/home.html', {
        'featured_events': featured_events,
        'categories': categories,
        'recommended_events': recommended_events,
        'total_events_count': total_events_count,
        'total_tickets_count': total_tickets_count,
        'total_cities_count': total_cities_count,
    })


def about_view(request):
    total_events = Event.objects.filter(status=Event.Status.PUBLISHED).count()
    total_cities = Event.objects.filter(
        status=Event.Status.PUBLISHED
    ).values_list('city', flat=True).distinct().count()
    return render(request, 'pages/about.html', {
        'total_events': total_events,
        'total_cities': total_cities,
    })


from .models import ContactMessage


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )

        messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        return redirect('contact')
    return render(request, 'pages/contact.html')

def careers_view(request):
    return render(request, 'pages/careers.html')

from django.contrib.auth.decorators import login_required


@login_required
def contact_messages_view(request):
    if request.user.role != 'ORGANIZER':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    submitted_messages = ContactMessage.objects.all()
    return render(request, 'pages/contact_messages.html', {'messages_list': submitted_messages})