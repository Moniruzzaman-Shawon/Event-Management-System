from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from events.models import Event
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from users.models import CustomUser
from django.views.generic import DeleteView
from django.views.generic import ListView
from .forms import CustomPasswordResetForm  

from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)



User = get_user_model()

def is_admin_group(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()

def is_organizer(user):
    return is_admin_group(user) or user.groups.filter(name="Organizer").exists()

def is_participant(user):
    return is_admin_group(user) or user.groups.filter(name="Participant").exists()

def get_user_role(user):
    if user.groups.filter(name="Admin").exists():
        return "admin"
    elif user.groups.filter(name="Organizer").exists():
        return "organizer"
    elif user.groups.filter(name="Participant").exists():
        return "participant"
    return None


# Converted into Classed Based Views

class SignupView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "users/signup.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            participant_group, created = Group.objects.get_or_create(name='Participant')
            user.groups.add(participant_group)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activation_link = request.build_absolute_uri(
                reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
            )

            subject = "Activate your account"
            message = render_to_string('users/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            user_email = form.cleaned_data.get('email')
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)

            return render(request, "users/activation_sent.html")

        return render(request, "users/signup.html", {"form": form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'users/activation_invalid.html')

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            return render(self.request, 'users/activation_required.html')
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

@login_required
@user_passes_test(is_admin_group)
def promote_from_participants(request):
    participant_group = Group.objects.get(name="Participant")
    participants = User.objects.filter(groups=participant_group)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = get_object_or_404(User, id=user_id)
        organizer_group = Group.objects.get(name="Organizer")
        user.groups.remove(participant_group)
        user.groups.add(organizer_group)
        user.save()
        return redirect('promote_from_participants')

    return render(request, "users/promote_from_participants.html", {
        "participants": participants
    })



# Converted into Classed Based Views

class OrganizerListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "organizer/organizer_list.html"
    context_object_name = "organizers"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name="Admin").exists()

    def get_queryset(self):
        return User.objects.filter(groups__name="Organizer")


# Converted into Classed Based Views

# add organizer
class AddOrganizer(LoginRequiredMixin, UserPassesTestMixin, View): #add organizer
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name="Admin").exists()

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "organizer/add_organizer.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            organizer_group, _ = Group.objects.get_or_create(name="Organizer")
            user.groups.add(organizer_group)
            return redirect("organizer_list")
        return render(request, "organizer/add_organizer.html", {"form": form})


# edit organizer

# Converted into Classed Based Views
class EditOrganizer(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.groups.filter(name="Admin").exists()

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id, groups__name="Organizer")
        form = CustomUserChangeForm(instance=user)
        return render(request, "organizer/edit_organizer.html", {"form": form, "user": user})

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id, groups__name="Organizer")
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("organizer_list")
        return render(request, "organizer/edit_organizer.html", {"form": form, "user": user})


# Converted into Classed Based Views
class DeleteOrganizer(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = "organizer/delete_organizer_confirm.html"
    success_url = reverse_lazy("organizer_list")
    pk_url_kwarg = 'user_id'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name="Admin").exists()

    def get_object(self, queryset=None):
        user = get_object_or_404(User, id=self.kwargs.get(self.pk_url_kwarg), groups__name="Organizer")
        return user

@login_required
@user_passes_test(is_admin_group)
def organizer_detail(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Organizer")
    return render(request, "organizer/organizer_detail.html", {"user": user})

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

@login_required
@user_passes_test(is_admin_group)
def group_list(request):
    groups = Group.objects.all()
    return render(request, "groups/group_list.html", {"groups": groups})

@login_required
@user_passes_test(is_admin_group)
def add_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("group_list")
    else:
        form = GroupForm()
    return render(request, "groups/add_group.html", {"form": form})

@login_required
@user_passes_test(is_admin_group)
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

@login_required
@user_passes_test(is_admin_group)
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST":
        group.delete()
        return redirect("group_list")
    return render(request, "groups/delete_group_confirm.html", {"group": group})



# Converted into Classed Based Views

class AddParticipant(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name__in=["Admin", "Organizer"]).exists()

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "participants/add_participant.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            participant_group, _ = Group.objects.get_or_create(name="Participant")
            user.groups.add(participant_group)
            return redirect("participant_list")
        return render(request, "participants/add_participant.html", {"form": form})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def edit_participant(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Participant")
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("participant_list")
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, "participants/edit_participant.html", {"form": form, "user": user})


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def delete_participant(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Participant")
    if request.method == "POST":
        user.delete()
        return redirect("participant_list")
    return render(request, "participants/delete_participant_confirm.html", {"user": user})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def participant_detail(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Participant")
    return render(request, "participants/participant_detail.html", {"user": user})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def participant_list(request):
    participants = User.objects.filter(groups__name="Participant")
    return render(request, "participants/participant_list.html", {"participants": participants})

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    events = Event.objects.all()

    total_participants = User.objects.filter(groups__name="Participant").count()
    total_events = events.count()
    upcoming_events = events.filter(date__gte=timezone.now().date()).count()
    past_events = events.filter(date__lt=timezone.now().date()).count()

    context = {
        "total_participants": total_participants,
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
    }
    return render(request, "users/admin_dashboard.html", context)

@login_required
@user_passes_test(is_organizer)
def organizer_dashboard(request):
    events = Event.objects.all()

    total_participants = User.objects.filter(groups__name="Participant").count()
    total_events = events.count()
    upcoming_events = events.filter(date__gte=timezone.now().date()).count()
    past_events = events.filter(date__lt=timezone.now().date()).count()

    context = {
        "total_participants": total_participants,
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
    }
    return render(request, "users/organizer_dashboard.html", context)

@login_required
@user_passes_test(is_participant)
def participant_dashboard(request):
    user = request.user
    rsvped_events = Event.objects.filter(participants=user).order_by('date', 'time')
    return render(request, "users/participant_dashboard.html", {'rsvped_events': rsvped_events})




# Profile View
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "account/profile.html", {"user": request.user})


# Edit Profile View
class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = CustomUserChangeForm(instance=request.user)
        return render(request, "account/edit_profile.html", {"form": form})

    def post(self, request):
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request, "account/edit_profile.html", {"form": form})


# Password change views
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "account/change_password.html"
    success_url = reverse_lazy("password_change_done")


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "account/change_password_done.html"


# Password reset views (no login required)
class CustomPasswordResetView(PasswordResetView):
    template_name = "account/password_reset_form.html"
    email_template_name = "account/password_reset_email.html"
    subject_template_name = "account/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    form_class = CustomPasswordResetForm 


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "account/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "account/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "account/password_reset_complete.html"