from django.db.models import Q
from django.utils import timezone
from .models import Event


def get_recommended_events(user, limit=4):
    """
    Recommend events based on categories the user has shown interest in
    (via bookings, favorites, or reviews). Falls back to upcoming events
    if the user has no interaction history yet.
    """
    if not user.is_authenticated:
        return Event.objects.filter(
            status=Event.Status.PUBLISHED,
            event_date__gte=timezone.now().date()
        ).order_by('event_date')[:limit]

    # Collect category IDs from everything this user has interacted with
    booked_categories = Event.objects.filter(
        bookings__user=user
    ).values_list('category_id', flat=True)

    favorited_categories = Event.objects.filter(
        favorited_by__user=user
    ).values_list('category_id', flat=True)

    reviewed_categories = Event.objects.filter(
        reviews__user=user
    ).values_list('category_id', flat=True)

    interest_category_ids = set(booked_categories) | set(favorited_categories) | set(reviewed_categories)
    interest_category_ids.discard(None)

    # Events the user has already booked — don't recommend those again
    already_booked_event_ids = Event.objects.filter(
        bookings__user=user
    ).values_list('id', flat=True)

    base_queryset = Event.objects.filter(
        status=Event.Status.PUBLISHED,
        event_date__gte=timezone.now().date()
    ).exclude(
        id__in=already_booked_event_ids
    ).exclude(
        organizer=user
    )

    if interest_category_ids:
        recommended = base_queryset.filter(
            category_id__in=interest_category_ids
        ).order_by('event_date')[:limit]

        # If category-based matches aren't enough to fill the limit, pad with general upcoming events
        if recommended.count() < limit:
            remaining = limit - recommended.count()
            extra = base_queryset.exclude(
                id__in=[e.id for e in recommended]
            ).order_by('event_date')[:remaining]
            return list(recommended) + list(extra)

        return recommended

    # No interaction history yet — just show upcoming events
    return base_queryset.order_by('event_date')[:limit]