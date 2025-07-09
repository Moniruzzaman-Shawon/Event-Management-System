from django.urls import path
from .views import signup_view, CustomLoginView, CustomLogoutView, admin_dashboard, participant_dashboard, organizer_dashboard

urlpatterns = [
    path("sign-up/", signup_view, name="signup"),
    path("sign-in/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/organizer/", organizer_dashboard, name="organizer_dashboard"),
    path("dashboard/participant/", participant_dashboard, name="participant_dashboard"),
]
