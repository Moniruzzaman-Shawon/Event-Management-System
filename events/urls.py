from django.urls import path
from events.views import (
    show_event,
    dashboard_view,
    add_event,
    all_events,
    search_events,
    edit_event,
    delete_event,
    category_list,
    add_category,
    edit_category,
    delete_category
)

urlpatterns = [
    path('show_event/', show_event),
    path('dashboard/', dashboard_view, name='dashboard'),    
    path('add_event/', add_event, name='add_event'),
    path('all_events/', all_events, name='all_events'),
    path('search/', search_events, name='search_events'),
    path('edit_event/<int:event_id>/', edit_event, name='edit_event'),
    path('delete_event/<int:event_id>/', delete_event, name='delete_event'),
    path('categories/', category_list, name='category_list'),
    path('categories/add/', add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', delete_category, name='delete_category'),
]
