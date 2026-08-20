from rest_framework import serializers
from events.models import Event, Category
from tickets.models import TicketType
from reviews.models import Review
from bookings.models import Booking, BookingItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'available_quantity']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'comment', 'created_at']


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the event list endpoint."""
    category = CategorySerializer(read_only=True)
    organizer_name = serializers.CharField(source='organizer.username', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'category', 'organizer_name',
            'event_date', 'start_time', 'city', 'venue', 'image',
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single event, including nested ticket types and reviews."""
    category = CategorySerializer(read_only=True)
    organizer_name = serializers.CharField(source='organizer.username', read_only=True)
    ticket_types = TicketTypeSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'organizer_name',
            'event_date', 'start_time', 'venue', 'city', 'image',
            'ticket_types', 'reviews', 'average_rating',
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)


    from bookings.models import Booking, BookingItem


class BookingItemSerializer(serializers.ModelSerializer):
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)

    class Meta:
        model = BookingItem
        fields = ['id', 'ticket_type_name', 'quantity', 'price', 'subtotal']


class BookingSerializer(serializers.ModelSerializer):
    """Used for GET /api/my-bookings/ — read-only display of existing bookings."""
    event_title = serializers.CharField(source='event.title', read_only=True)
    items = BookingItemSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'event_title', 'booking_date', 'total_amount', 'status', 'items']


class BookingCreateSerializer(serializers.Serializer):
    """Used for POST /api/bookings/ — validates input for creating a new booking."""
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)