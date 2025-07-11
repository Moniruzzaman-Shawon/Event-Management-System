from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.utils import timezone
from django import forms

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from events.models import Event



# Group check utility
def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()

def is_organizer(user):
    return is_admin(user) or user.groups.filter(name="Organizer").exists()

def is_participant(user):
    return is_admin(user) or user.groups.filter(name="Participant").exists()


def get_user_role(user):
    if user.groups.filter(name="Admin").exists():
        return "admin"
    elif user.groups.filter(name="Organizer").exists():
        return "organizer"
    elif user.groups.filter(name="Participant").exists():
        return "participant"
    return None


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            participant_group, _ = Group.objects.get_or_create(name="Participant")
            user.groups.add(participant_group)
            login(request, user)
            role = get_user_role(user)
            if role == "admin":
                return redirect("admin_dashboard")
            elif role == "organizer":
                return redirect("organizer_dashboard")
            elif role == "participant":
                return redirect("participant_dashboard")
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/signup.html", {"form": form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        role = get_user_role(user)
        if role == "admin":
            return redirect("admin_dashboard")
        elif role == "organizer":
            return redirect("organizer_dashboard")
        elif role == "participant":
            return redirect("participant_dashboard")
        return redirect("home")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")


# participant_list
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def participant_list(request):
    participants = User.objects.filter(groups__name="Participant")
    return render(request, "users/participant_list.html", {"participants": participants})

# organizer_list
@login_required
@user_passes_test(is_admin)
def organizer_list(request):
    organizers = User.objects.filter(groups__name="Organizer")
    return render(request, "organizer/organizer_list.html", {"organizers": organizers})

# Add Organizer
@login_required
@user_passes_test(is_admin)
def add_organizer(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            organizer_group, _ = Group.objects.get_or_create(name="Organizer")
            user.groups.add(organizer_group)
            return redirect("organizer_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "organizer/add_organizer.html", {"form": form})


# Edit Organizer
@login_required
@user_passes_test(is_admin)
def edit_organizer(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Organizer")
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("organizer_list")
    else:
        form = UserChangeForm(instance=user)
    return render(request, "organizer/edit_organizer.html", {"form": form, "user": user})


# Delete Organizer
@login_required
@user_passes_test(is_admin)
def delete_organizer(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Organizer")
    if request.method == "POST":
        user.delete()
        return redirect("organizer_list")
    return render(request, "organizer/delete_organizer_confirm.html", {"user": user})


# Organizer detail view 
@login_required
@user_passes_test(is_admin)
def organizer_detail(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Organizer")
    return render(request, "organizer/organizer_detail.html", {"user": user})


 # Group form for update (name only)
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']


# List all groups
@login_required
@user_passes_test(is_admin)
def group_list(request):
    groups = Group.objects.all()
    return render(request, "groups/group_list.html", {"groups": groups})


# Add new group
@login_required
@user_passes_test(is_admin)
def add_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("group_list")
    else:
        form = GroupForm()
    return render(request, "groups/add_group.html", {"form": form})


# Edit group
@login_required
@user_passes_test(is_admin)
def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("group_list")
    else:
        form = GroupForm(instance=group)
    return render(request, "groups/edit_group.html", {"form": form, "group": group})


# Delete group
@login_required
@user_passes_test(is_admin)
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST":
        group.delete()
        return redirect("group_list")
    return render(request, "groups/delete_group_confirm.html", {"group": group})


# edit_participant

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def edit_participant(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Participant")
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("participant_list")
    else:
        form = UserChangeForm(instance=user)
    return render(request, "users/edit_participant.html", {"form": form, "user": user})


# delete_participant
@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def delete_participant(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Participant")
    if request.method == "POST":
        user.delete()
        return redirect("participant_list")
    return render(request, "users/delete_participant_confirm.html", {"user": user})



# ---------------dashboard----------------

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")


@login_required
@user_passes_test(is_organizer)
def organizer_dashboard(request):
    today = timezone.localdate()
    events = Event.objects.filter(creator=request.user).prefetch_related('participants').order_by('date', 'time')
    total_events = events.count()
    upcoming_events = events.filter(date__gt=today).count()
    past_events = events.filter(date__lt=today).count()
    total_participants = sum(event.participants.count() for event in events)

    context = {
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "total_participants": total_participants,
        "events": events,
        "today": today,
    }
    return render(request, "users/organizer_dashboard.html", context)


@login_required
@user_passes_test(is_participant)
def participant_dashboard(request):
    user = request.user
    rsvped_events = Event.objects.filter(participants=user).order_by('date', 'time')

    context = {
        'rsvped_events': rsvped_events,
    }
    return render(request, "users/participant_dashboard.html", context)

