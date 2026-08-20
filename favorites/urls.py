from django.urls import path
from . import views

urlpatterns = [
    path('toggle/<int:event_pk>/', views.toggle_favorite_view, name='toggle_favorite'),
    path('my-favorites/', views.my_favorites_view, name='my_favorites'),
]