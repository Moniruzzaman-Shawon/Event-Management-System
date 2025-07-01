from django.shortcuts import render,redirect
from django.utils import timezone
from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm
from django.shortcuts import get_object_or_404, redirect, render




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

def dashboard_view(request):
    today = timezone.localdate()

    # Calculate stats
    total_events = Event.objects.count()
    total_participants = Participant.objects.count()  
    upcoming_events = Event.objects.filter(date__gt=today).count()
    past_events = Event.objects.filter(date__lt=today).count()

    # filter type from query params (default = today)
    filter_type = request.GET.get("type", "today")

    if filter_type == "all":
        events = Event.objects.all()
    elif filter_type == "upcoming":
        events = Event.objects.filter(date__gt=today)
    elif filter_type == "past":
        events = Event.objects.filter(date__lt=today)
    else:
        events = Event.objects.filter(date=today)

    # Prefetch participants to optimize DB queries
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
    return render(request, "dashboard/dashboard_view.html", context)

    # add a new event
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)

        # Get new participant info from form
        new_participant_name = request.POST.get('new_participant_name')
        new_participant_email = request.POST.get('new_participant_email')

        if form.is_valid():
            event = form.save()

            # Create and add new participant if both fields provided
            if new_participant_name and new_participant_email:
                participant, created = Participant.objects.get_or_create(
                    email=new_participant_email,
                    defaults={'name': new_participant_name}
                )
                event.participants.add(participant)

            return redirect('dashboard')
    else:
        form = EventForm()

    return render(request, 'events/add_event.html', {'form': form})

# show all 
def all_events(request):
    events = Event.objects.select_related('category').prefetch_related('participants').order_by('-date', '-time')
    return render(request, 'events/all_events.html', {'events': events})

# search event
def search_events(request):
    query = request.GET.get('q', '')
    events = Event.objects.all()

    if query:
        events = events.filter(name__icontains=query)

    return render(request, 'events/search_events.html', {
        'events': events,
        'query': query,
    })

# update event
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


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.delete()
        return redirect('dashboard')

    return render(request, 'events/delete_event_confirm.html', {'event': event})


# List participants
def participant_list(request):
    participants = Participant.objects.all()
    return render(request, "participants/participant_list.html", {"participants": participants})

# Add participant
def add_participant(request):
    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('participant_list')
    else:
        form = ParticipantForm()
    return render(request, "participants/add_participant.html", {"form": form})

# Edit participant
def edit_participant(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    if request.method == "POST":
        form = ParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            return redirect('participant_list')
    else:
        form = ParticipantForm(instance=participant)
    return render(request, "participants/edit_participant.html", {"form": form})

# Delete participant


def delete_participant(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    
    if request.method == 'POST':
        participant.delete()
        return redirect('participant_list')

    return render(request, 'participants/delete_participant_confirm.html', {'participant': participant})

# List all categories
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})

# Add category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/add_category.html', {'form': form})

# Edit category
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

# Delete category
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'categories/delete_category_confirm.html', {'category': category})