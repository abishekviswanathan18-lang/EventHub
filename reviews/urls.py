from django.urls import path
from . import views

urlpatterns = [
    path('event/<int:event_pk>/add/', views.add_review_view, name='add_review'),
]