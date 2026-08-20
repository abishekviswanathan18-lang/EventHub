from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:ticket_type_pk>/', views.create_booking_view, name='create_booking'),
    path('<int:pk>/', views.booking_detail_view, name='booking_detail'),
    path('<int:pk>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('manage/', views.organizer_bookings_view, name='organizer_bookings'),
    path('refund/<int:refund_pk>/process/', views.process_refund_view, name='process_refund'),
]