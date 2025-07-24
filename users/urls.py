from django.urls import path
from users import views
from .views import (CustomLoginView, CustomLogoutView, admin_dashboard, 
                    participant_dashboard, organizer_dashboard, 
                     edit_participant, delete_participant,  
                     group_list, organizer_detail, add_group,
                     edit_group, delete_group,  participant_detail, participant_list,
                     activate_account
)
from django.conf import settings
from django.conf.urls.static import static
from users.views import EditOrganizer, DeleteOrganizer, AddParticipant, SignupView, OrganizerListView, AddOrganizer

urlpatterns = [
        
    # Auth

    # path("sign-up/", signup_view, name="signup"),
    path("sign-up/", SignupView.as_view(), name="signup"),
    path("sign-in/", CustomLoginView.as_view(), name="login"),
    path("users/logout/", CustomLogoutView.as_view(), name="logout"),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    

    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/organizer/", organizer_dashboard, name="organizer_dashboard"),
    path("dashboard/participant/", participant_dashboard, name="participant_dashboard"),
    
    # Organizers

    # path('organizers/', organizer_list, name='organizer_list'),
    path('organizers/', OrganizerListView.as_view(), name='organizer_list'),
    # path('organizers/add/', add_organizer, name='add_organizer'),
    path('organizers/add/', AddOrganizer.as_view(), name='add_organizer'),
    # path('organizers/edit/<int:user_id>/', edit_organizer, name='edit_organizer'),
    path('organizer/edit/<int:user_id>/', EditOrganizer.as_view(), name='edit_organizer'),
    # path('organizers/delete/<int:user_id>/', delete_organizer, name='delete_organizer'),
    path('organizers/delete/<int:user_id>/', DeleteOrganizer.as_view(), name='delete_organizer'),

    path('organizers/<int:user_id>/', organizer_detail, name='organizer_detail'),
    path('promote-participant/', views.promote_from_participants, name='promote_from_participants'),


    # Groups

    path('groups/', group_list, name='group_list'),
    path('groups/add/', add_group, name='add_group'),
    path('groups/edit/<int:group_id>/', edit_group, name='edit_group'),
    path('groups/delete/<int:group_id>/', delete_group, name='delete_group'),

    # Participants

    path('participants/', participant_list, name='participant_list'),
    # path('participants/add/', add_participant, name='add_participant'),
    path('participants/add/', AddParticipant.as_view(), name='add_participant'),
    path('participants/edit/<int:user_id>/', edit_participant, name='edit_participant'),
    path('participants/delete/<int:user_id>/', delete_participant, name='delete_participant'),
    path('participants/<int:user_id>/', participant_detail, name='participant_detail'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)