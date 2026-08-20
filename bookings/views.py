from .models import Booking, BookingItem, Refund

from .emails import send_booking_confirmation_email

from checkin.models import Ticket

from django.utils import timezone
from datetime import datetime, timedelta
from tickets.models import TicketType

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from tickets.models import TicketType
from .models import Booking, BookingItem
from .forms import BookingForm

from django.urls import reverse

@login_required
def create_booking_view(request, ticket_type_pk):
    ticket_type = get_object_or_404(TicketType, pk=ticket_type_pk)
    event = ticket_type.event

    if request.user == event.organizer:
        messages.error(request, "You can't book tickets for your own event.")
        return redirect('event_detail', pk=event.pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            with transaction.atomic():
                # Lock this ticket type's row so two simultaneous bookings
                # can't both read the same "available_quantity" and oversell
                locked_ticket = TicketType.objects.select_for_update().get(pk=ticket_type.pk)

                if quantity > locked_ticket.available_quantity:
                    messages.error(
                        request,
                        f'Only {locked_ticket.available_quantity} tickets available.'
                    )
                    return redirect('event_detail', pk=event.pk)

                subtotal = locked_ticket.price * quantity

                booking = Booking.objects.create(
                    user=request.user,
                    event=event,
                    total_amount=subtotal,
                    status=Booking.Status.CONFIRMED
                )
                booking_item = BookingItem.objects.create(
                    booking=booking,
                    ticket_type=locked_ticket,
                    quantity=quantity,
                    price=locked_ticket.price,
                    subtotal=subtotal
                )

                # Create one individual Ticket (with its own QR code) per unit purchased
                for _ in range(quantity):
                    Ticket.objects.create(booking_item=booking_item)

            locked_ticket.available_quantity -= quantity
            locked_ticket.save()

            send_booking_confirmation_email(booking)

            messages.success(request, 'Booking confirmed!')
            return redirect(f"{reverse('booking_detail', kwargs={'pk': booking.pk})}?new=true")
    else:
        form = BookingForm()

    return render(request, 'bookings/booking_form.html', {'form': form, 'ticket_type': ticket_type, 'event': event})


@login_required
def booking_detail_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if booking.status == Booking.Status.CANCELLED:
        messages.error(request, 'This booking is already cancelled.')
        return redirect('booking_detail', pk=booking.pk)

    # Combine event_date + start_time into one timezone-aware datetime
    event_datetime = timezone.make_aware(
        datetime.combine(booking.event.event_date, booking.event.start_time)
    )
    cutoff = event_datetime - timedelta(hours=24)

    if timezone.now() > cutoff:
        messages.error(request, 'Cancellation is only allowed up to 24 hours before the event.')
        return redirect('booking_detail', pk=booking.pk)

    if request.method == 'POST':
        with transaction.atomic():
            for item in booking.items.all():
                locked_ticket = TicketType.objects.select_for_update().get(pk=item.ticket_type.pk)
                locked_ticket.available_quantity += item.quantity
                locked_ticket.save()

            booking.status = Booking.Status.CANCELLED
            booking.save()

            Refund.objects.create(
                booking=booking,
                amount=booking.total_amount,
                status=Refund.Status.PENDING
            )

        messages.success(request, 'Booking cancelled. Your refund is being processed.')
        return redirect('booking_detail', pk=booking.pk)

    return render(request, 'bookings/booking_cancel_confirm.html', {'booking': booking, 'cutoff': cutoff})


@login_required
def organizer_bookings_view(request):
    if request.user.role != 'ORGANIZER':
        messages.error(request, 'Only organizers can view this page.')
        return redirect('home')

    bookings = Booking.objects.filter(
        event__organizer=request.user
    ).select_related('event', 'user').order_by('-booking_date')

    return render(request, 'bookings/organizer_bookings.html', {'bookings': bookings})


@login_required
def process_refund_view(request, refund_pk):
    refund = get_object_or_404(Refund, pk=refund_pk)

    if refund.booking.event.organizer != request.user:
        messages.error(request, 'You can only process refunds for your own events.')
        return redirect('organizer_bookings')

    if request.method == 'POST':
        from django.utils import timezone
        refund.status = Refund.Status.PROCESSED
        refund.processed_at = timezone.now()
        refund.save()
        messages.success(request, 'Refund marked as processed.')

    return redirect('organizer_bookings')