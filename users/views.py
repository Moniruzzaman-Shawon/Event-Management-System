from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .utils import get_user_role

# Utility to get user role from groups
def get_user_role(user):
    if user.groups.filter(name="Admin").exists():
        return "admin"
    elif user.groups.filter(name="Organizer").exists():
        return "organizer"
    elif user.groups.filter(name="Participant").exists():
        return "participant"
    return None

#  Signup View
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Assign user to Participant group by default
            participant_group, created = Group.objects.get_or_create(name="Participant")
            user.groups.add(participant_group)

            login(request, user)

            role = get_user_role(user)
            if role == "admin":
                return redirect("admin_dashboard")
            elif role == "organizer":
                return redirect("organizer_dashboard")
            elif role == "participant":
                return redirect("participant_dashboard")
            else:
                return redirect("home")  # fallback
    else:
        form = CustomUserCreationForm()
    return render(request, "users/signup.html", {"form": form})
#  Custom Login View with redirect to dashboard
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

# Logout View
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")  # redirect to login page after logout


#  DASHBOARD VIEWS
@login_required
@user_passes_test(lambda u: u.groups.filter(name="Admin").exists())
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")

@login_required
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
def organizer_dashboard(request):
    return render(request, "users/organizer_dashboard.html")

@login_required
@user_passes_test(lambda u: u.groups.filter(name="Participant").exists())
def participant_dashboard(request):
    return render(request, "users/participant_dashboard.html")
