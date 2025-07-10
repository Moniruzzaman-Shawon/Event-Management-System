from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from events.views import home, contact, aboutUs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('contact/', contact),
    path('aboutus/', aboutUs),
    path('events/', include("events.urls")),     
    path('', include("users.urls")),     
    path('', include('events.urls')),        
]

# Optional: Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
