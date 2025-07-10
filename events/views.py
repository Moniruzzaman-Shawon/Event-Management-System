from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Event, Category
from .forms import EventForm, CategoryForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User  # Import User model


def home(request):
    return render(request, "home.html")


def contact(request):
    return render(request, "contact.html")


def aboutUs(request):
    return render(request, "aboutus.html")


def events(request):
    return render(request, "events.html")


def show_event(request):
    return render(request, "show_event.html")


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
def dashboard_view(request):
    if not request.user.groups.filter(name="Organizer").exists():
        raise PermissionDenied  # Or redirect

    today = timezone.localdate()

    # Calculate stats
    total_events = Event.objects.count()
    total_participants = User.objects.filter(groups__name='Participant').count()  # count Users in Participant group
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()

    # Filter type from query params (default = today)
    filter_type = request.GET.get("type", "today")

    if filter_type == "all":
        events = Event.objects.all()
    elif filter_type == "upcoming":
        events = Event.objects.filter(date__gt=today)
    elif filter_type == "past":
        events = Event.objects.filter(date__lt=today)
    else:
        events = Event.objects.filter(date=today)

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
    return render(request, "events/dashboard_view.html", context)


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)

        # If you want to add participants here, now participants are Users
        # You can add logic for RSVP later

        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user  # Assign creator as current user
            event.save()

            # Handle ManyToMany participants if needed
            participant_ids = request.POST.getlist('participants')  # Expect participant user IDs
            if participant_ids:
                users = User.objects.filter(id__in=participant_ids)
                event.participants.set(users)

            return redirect('dashboard')
    else:
        form = EventForm()

    return render(request, 'events/add_event.html', {'form': form})


def all_events(request):
    events = Event.objects.select_related('category').prefetch_related('participants').order_by('-date', '-time')
    return render(request, 'events/all_events.html', {'events': events})


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
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.delete()
        return redirect('dashboard')

    return render(request, 'events/delete_event_confirm.html', {'event': event})


# Participant related views removed since Participant model is removed
# You should now manage participants as User model instances with group "Participant"


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
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
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
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
@user_passes_test(lambda u: u.groups.filter(name="Organizer").exists())
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'categories/delete_category_confirm.html', {'category': category})
