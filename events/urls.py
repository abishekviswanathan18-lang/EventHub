from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list_view, name='event_list'),
    path('create/', views.event_create_view, name='event_create'),
    path('dashboard/', views.organizer_dashboard_view, name='organizer_dashboard'),
    path('search-suggestions/', views.event_search_suggestions_view, name='event_search_suggestions'),
    path('image/<int:image_pk>/delete/', views.delete_event_image_view, name='delete_event_image'),
    path('<int:pk>/', views.event_detail_view, name='event_detail'),
    path('<int:pk>/edit/', views.event_edit_view, name='event_edit'),
    path('<int:pk>/delete/', views.event_delete_view, name='event_delete'),
    path('<int:event_pk>/add-image/', views.add_event_image_view, name='add_event_image'),
]