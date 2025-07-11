from django.urls import path
from .views import (signup_view, CustomLoginView, CustomLogoutView, admin_dashboard, 
                    participant_dashboard, organizer_dashboard, 
                     edit_participant, delete_participant, organizer_list, add_organizer,
                     edit_organizer, delete_organizer , group_list, organizer_detail, add_group,
                     edit_group, delete_group, add_participant, participant_detail, participant_list,
                     activate_account,
)
urlpatterns = [
        
    # Auth

    path("sign-up/", signup_view, name="signup"),
    path("sign-in/", CustomLoginView.as_view(), name="login"),
    path("users/logout/", CustomLogoutView.as_view(), name="logout"),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    # Dashboards

    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/organizer/", organizer_dashboard, name="organizer_dashboard"),
    path("dashboard/participant/", participant_dashboard, name="participant_dashboard"),
    
    # Organizers

    path('organizers/', organizer_list, name='organizer_list'),
    path('organizers/add/', add_organizer, name='add_organizer'),
    path('organizers/edit/<int:user_id>/', edit_organizer, name='edit_organizer'),
    path('organizers/delete/<int:user_id>/', delete_organizer, name='delete_organizer'),
    path('organizers/<int:user_id>/', organizer_detail, name='organizer_detail'),

    # Groups

    path('groups/', group_list, name='group_list'),
    path('groups/add/', add_group, name='add_group'),
    path('groups/edit/<int:group_id>/', edit_group, name='edit_group'),
    path('groups/delete/<int:group_id>/', delete_group, name='delete_group'),

    # Participants

    path('participants/', participant_list, name='participant_list'),
    path('participants/add/', add_participant, name='add_participant'),
    path('participants/edit/<int:user_id>/', edit_participant, name='edit_participant'),
    path('participants/delete/<int:user_id>/', delete_participant, name='delete_participant'),
    path('participants/<int:user_id>/', participant_detail, name='participant_detail'),

]