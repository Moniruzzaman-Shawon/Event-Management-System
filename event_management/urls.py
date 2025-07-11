from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from events.views import home, contact, aboutUs
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('contact/', contact),
    path('aboutus/', aboutUs),
    path('events/', include("events.urls")),     
    path('', include("users.urls")),     
    path('', include('events.urls')),        
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
