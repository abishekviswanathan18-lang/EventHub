from django.urls import path
from . import views

urlpatterns = [
    path('event/<int:event_pk>/scan/', views.checkin_scan_view, name='checkin_scan'),
]