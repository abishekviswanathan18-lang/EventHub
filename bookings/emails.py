from django.core.mail import send_mail
from django.conf import settings


def send_booking_confirmation_email(booking):
    subject = f'Booking Confirmed - {booking.event.title}'

    items_text = '\n'.join(
        f'  {item.ticket_type.name} x {item.quantity} — ₹{item.subtotal}'
        for item in booking.items.all()
    )

    message = f"""Hi {booking.user.username},

Your booking is confirmed! Here are the details:

Booking ID: EVT-{booking.id:05d}
Event: {booking.event.title}
Date: {booking.event.event_date}
Time: {booking.event.start_time}
Venue: {booking.event.venue}, {booking.event.city}

Tickets:
{items_text}

Total Paid: ₹{booking.total_amount}

Thank you for booking with EventHub!
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.user.email],
        fail_silently=False,
    )
    