from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from events.models import Event
from django.contrib.auth.forms import UserChangeForm


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

