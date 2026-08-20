from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('careers/', views.careers_view, name='careers'),
    path('messages/', views.contact_messages_view, name='contact_messages'),
]