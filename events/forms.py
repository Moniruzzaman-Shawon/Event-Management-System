from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category', 'participants']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'participants': forms.SelectMultiple(attrs={'size': 6}),
        }
