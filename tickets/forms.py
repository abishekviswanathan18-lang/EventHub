from django import forms
from .models import TicketType


class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = ['name', 'price', 'total_quantity']