from django import forms
from .models import Event, EventImage


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['category', 'title', 'description', 'event_date', 'start_time', 'venue', 'city', 'image']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class EventImageForm(forms.ModelForm):
    class Meta:
        model = EventImage
        fields = ['image']