from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.utils import timezone

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from events.models import Event


# Utility to get user role based on groups
def get_user_role(user):
    if user.groups.filter(name="Admin").exists():
        return "admin"
    elif user.groups.filter(name="Organizer").exists():
        return "organizer"
    elif user.groups.filter(name="Participant").exists():
        return "participant"
    return None


# Signup view
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add new user to Participant group by default
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
            return redirect("home")  # fallback redirect
    else:
        form = CustomUserCreationForm()
    return render(request, "users/signup.html", {"form": form})


# Custom login view with redirect by role
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


# Logout view
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")


# Admin dashboard view
@login_required
@user_passes_test(lambda u: u.groups.filter(name="Admin").exists())
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")


# Organizer dashboard view
@login_required
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
def organizer_dashboard(request):
    today = timezone.localdate()

    # Fetch events created by the organizer
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


# Participant dashboard view
@login_required
@user_passes_test(lambda u: u.groups.filter(name="Participant").exists())
def participant_dashboard(request):
    return render(request, "users/participant_dashboard.html")


# Redirect user to dashboard after login based on role
@login_required
def dashboard_redirect(request):
    user = request.user
    if user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant_dashboard')
    elif user.is_superuser or user.groups.filter(name='Admin').exists():
        return redirect('admin_dashboard')
    else:
        return redirect('home')  # Or any fallback view
