from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Ticket


@login_required
def checkin_scan_view(request, event_pk):
    from events.models import Event
    event = get_object_or_404(Event, pk=event_pk)

    if event.organizer != request.user:
        messages.error(request, 'Only the event organizer can check in attendees.')
        return redirect('event_detail', pk=event.pk)

    result = None

    if request.method == 'POST':
        ticket_number = request.POST.get('ticket_number', '').strip()

        try:
            ticket = Ticket.objects.get(ticket_number=ticket_number)

            # Make sure this ticket actually belongs to THIS event
            if ticket.booking_item.ticket_type.event != event:
                result = {'status': 'wrong_event'}
            elif ticket.is_checked_in:
                result = {'status': 'already_used', 'ticket': ticket}
            else:
                ticket.is_checked_in = True
                ticket.checked_in_at = timezone.now()
                ticket.save()
                result = {'status': 'success', 'ticket': ticket}

        except (Ticket.DoesNotExist, ValueError):
            result = {'status': 'not_found'}

    return render(request, 'checkin/scan.html', {'event': event, 'result': result})