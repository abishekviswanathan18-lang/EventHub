from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from events.models import Event
from .forms import TicketTypeForm


@login_required
def ticket_type_create_view(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if event.organizer != request.user:
        messages.error(request, 'You can only add tickets to your own events.')
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = TicketTypeForm(request.POST)
        if form.is_valid():
            ticket_type = form.save(commit=False)
            ticket_type.event = event
            ticket_type.save()
            messages.success(request, f'Ticket type "{ticket_type.name}" added!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = TicketTypeForm()

    return render(request, 'tickets/ticket_type_form.html', {'form': form, 'event': event})