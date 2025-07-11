from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.utils import timezone
from django import forms
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from events.models import Event
from django.conf import settings  


# Group check utilities
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


# Signup with email activation
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # deactivate until email confirmation
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
    else:
        form = CustomUserCreationForm()
    return render(request, "users/signup.html", {"form": form})


# Activation view
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
        return redirect('home')  # redirect to dashboard or homepage
    else:
        return render(request, 'users/activation_invalid.html')


# Custom Login and Logout Views
class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            # Prevent inactive user login
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


# Organizer management - Admin only
@login_required
@user_passes_test(is_admin)
def organizer_list(request):
    organizers = User.objects.filter(groups__name="Organizer")
    return render(request, "organizer/organizer_list.html", {"organizers": organizers})

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

@login_required
@user_passes_test(is_admin)
def delete_organizer(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Organizer")
    if request.method == "POST":
        user.delete()
        return redirect("organizer_list")
    return render(request, "organizer/delete_organizer_confirm.html", {"user": user})

@login_required
@user_passes_test(is_admin)
def organizer_detail(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Organizer")
    return render(request, "organizer/organizer_detail.html", {"user": user})


# Group management - Admin only
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

@login_required
@user_passes_test(is_admin)
def group_list(request):
    groups = Group.objects.all()
    return render(request, "groups/group_list.html", {"groups": groups})

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

@login_required
@user_passes_test(is_admin)
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST":
        group.delete()
        return redirect("group_list")
    return render(request, "groups/delete_group_confirm.html", {"group": group})


# Participant management - Admin and Organizer
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def add_participant(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            participant_group, _ = Group.objects.get_or_create(name="Participant")
            user.groups.add(participant_group)
            return redirect("participant_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "participants/add_participant.html", {"form": form})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name__in=["Admin", "Organizer"]).exists())
def edit_participant(request, user_id):
    user = get_object_or_404(User, id=user_id, groups__name="Participant")
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("participant_list")
    else:
        form = UserChangeForm(instance=user)
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


# Dashboards
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    events = Event.objects.all()  # Admin sees all events

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
    # Filter events created by the organizer
    events = Event.objects.filter(creator=request.user)

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
