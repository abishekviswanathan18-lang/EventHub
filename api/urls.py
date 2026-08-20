from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import EventViewSet, my_bookings_api_view, create_booking_api_view

router = DefaultRouter()
router.register('events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('my-bookings/', my_bookings_api_view, name='api-my-bookings'),
    path('bookings/', create_booking_api_view, name='api-create-booking'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]