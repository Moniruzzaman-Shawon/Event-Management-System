from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from .models import Event, Category
from .forms import EventForm, CategoryForm
from django.conf import settings
from .models import Event
from django.contrib import messages
from django.contrib.auth import get_user_model


User = get_user_model()




# Group check utilities
def is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()

def is_organizer(user):
    return is_admin(user) or user.groups.filter(name="Organizer").exists()

def is_participant(user):
    return is_admin(user) or user.groups.filter(name="Participant").exists()


def home(request):
    return render(request, "home.html")


def contact(request):
    return render(request, "contact.html")


def aboutUs(request):
    return render(request, "aboutus.html")


def events(request):
    return render(request, "events.html")


def show_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/show_event.html', {'event': event})


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_superuser:
        return redirect('admin_dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant_dashboard')
    else:
        return redirect('dashboard')






@login_required
def dashboard_view(request):
    today = timezone.localdate()

    if request.user.groups.filter(name="Organizer").exists() or request.user.is_superuser:
        # Show all events for both Admin and Organizer
        user_events = Event.objects.all()
    else:
        # Show only relevant data to participants
        user_events = Event.objects.filter(creator=request.user)


    total_events = user_events.count()
    total_participants = User.objects.filter(groups__name='Participant').count()
    upcoming_events = user_events.filter(date__gt=today).count()
    past_events = user_events.filter(date__lt=today).count()

    filter_type = request.GET.get("type", "today")

    if filter_type == "all":
        events = user_events
    elif filter_type == "upcoming":
        events = user_events.filter(date__gt=today)
    elif filter_type == "past":
        events = user_events.filter(date__lt=today)
    else:
        events = user_events.filter(date=today)

    events = events.prefetch_related('participants').order_by('date', 'time')

    context = {
        "total_events": total_events,
        "total_participants": total_participants,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "events": events,
        "filter_type": filter_type,
        "today": today,
    }
    return render(request, "users/organizer_dashboard.html", context)



def can_add_event(user):
    return user.is_superuser or user.groups.filter(name__in=["Organizer", "Admin"]).exists()


@login_required
@user_passes_test(can_add_event)
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()

            participant_ids = request.POST.getlist('participants')
            if participant_ids:
                users = User.objects.filter(id__in=participant_ids)
                event.participants.set(users)

            return redirect('dashboard')
    else:
        form = EventForm()

    return render(request, 'events/add_event.html', {'form': form})


@login_required
def all_events(request):
    user = request.user
    # Allow any logged in user to see events (participant, organizer, admin)
    events = Event.objects.select_related('category').prefetch_related('participants').order_by('-date', '-time')
    
    # Permission to add/edit event only for admins and organizers
    can_add_event = user.is_superuser or user.groups.filter(name__in=["Organizer", "Admin"]).exists()

    return render(request, 'events/all_events.html', {
        'events': events,
        'can_add_event': can_add_event,
    })

@login_required
@user_passes_test(is_participant)
def search_events(request):
    query = request.GET.get('q', '')
    events = Event.objects.all()

    if query:
        events = events.filter(name__icontains=query)

    return render(request, 'events/search_events.html', {
        'events': events,
        'query': query,
    })


@login_required
@user_passes_test(is_organizer)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
@user_passes_test(is_organizer)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.delete()
        return redirect('dashboard')

    return render(request, 'events/delete_event_confirm.html', {'event': event})


def is_organizer_or_admin(user):
    return user.is_superuser or user.groups.filter(name__in=["Organizer", "Admin"]).exists()

@login_required
@user_passes_test(is_organizer_or_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_organizer_or_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/add_category.html', {'form': form})


@login_required
@user_passes_test(is_organizer_or_admin)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'categories/edit_category.html', {'form': form, 'category': category})


@login_required
@user_passes_test(is_organizer_or_admin)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'categories/delete_category_confirm.html', {'category': category})

# RSVP
@login_required
@user_passes_test(is_participant)
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user
    
    if user in event.participants.all():
        messages.info(request, "You have already RSVP'd to this event.")
    else:
        event.participants.add(user)
        messages.success(request, "RSVP successful!")

        # Send confirmation email
        send_mail(
            subject=f"RSVP Confirmation for {event.name}",
            message=(
                f"Hi {user.first_name or user.username},\n\n"
                f"You have successfully RSVP'd to the event '{event.name}' scheduled on {event.date} at {event.time}.\n\n"
                "Thank you for your participation!"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

    return redirect('event_detail', event_id=event.id)


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    

    return render(request, 'events/event_detail.html', {'event': event})
