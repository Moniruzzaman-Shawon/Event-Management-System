from django.urls import path
from events.views import show_event

urlpatterns = [
    path('show_event/', show_event),
    
    
]