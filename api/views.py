

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from tickets.models import TicketType
from bookings.models import Booking, BookingItem
from checkin.models import Ticket
from .serializers import BookingSerializer, BookingCreateSerializer



from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from events.models import Event
from .serializers import EventListSerializer, EventDetailSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for browsing published events.

    list: Returns a paginated list of all published events.
    retrieve: Returns full details for a single event, including ticket types and reviews.
    """
    queryset = Event.objects.filter(status=Event.Status.PUBLISHED).order_by('event_date')
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'city']
    search_fields = ['title', 'description']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventDetailSerializer



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings_api_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking_api_view(request):
    serializer = BookingCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    ticket_type_id = serializer.validated_data['ticket_type_id']
    quantity = serializer.validated_data['quantity']

    ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
    event = ticket_type.event

    if request.user == event.organizer:
        return Response(
            {'error': "You can't book tickets for your own event."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        locked_ticket = TicketType.objects.select_for_update().get(pk=ticket_type.pk)

        if quantity > locked_ticket.available_quantity:
            return Response(
                {'error': f'Only {locked_ticket.available_quantity} tickets available.'},
                status=status.HTTP_400_BAD_REQUEST
            )

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

        for _ in range(quantity):
            Ticket.objects.create(booking_item=booking_item)

        locked_ticket.available_quantity -= quantity
        locked_ticket.save()

    return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)