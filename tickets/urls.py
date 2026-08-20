from django.urls import path
from . import views

urlpatterns = [
    path('event/<int:event_pk>/add/', views.ticket_type_create_view, name='ticket_type_create'),
]