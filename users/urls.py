from django.urls import path
from .views import signup_view, CustomLoginView, CustomLogoutView, admin_dashboard, participant_dashboard, organizer_dashboard, participant_list, edit_participant, delete_participant

urlpatterns = [
    path("sign-up/", signup_view, name="signup"),
    path("sign-in/", CustomLoginView.as_view(), name="login"),
    path("users/logout/", CustomLogoutView.as_view(), name="logout"),

    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/organizer/", organizer_dashboard, name="organizer_dashboard"),
    path("dashboard/participant/", participant_dashboard, name="participant_dashboard"),
    path("participants/", participant_list, name="participant_list"),
    path("participants/edit/<int:user_id>/", edit_participant, name="edit_participant"),
    path("participants/delete/<int:user_id>/", delete_participant, name="delete_participant"),
]