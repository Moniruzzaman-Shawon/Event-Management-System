from django.urls import path
from events.views import show_event, dashboard_view, add_event, all_events, search_events

urlpatterns = [
    path('show_event/', show_event),
    path('dashboard/', dashboard_view, name='dashboard'),    
    path('add_event/', add_event, name='add_event'),
    path('all_events/', all_events, name='all_events'),
    path('search/', search_events, name='search_events'),

]