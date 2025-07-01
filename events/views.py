from django.shortcuts import render
from django.utils import timezone
from .models import Event, Participant, Category
from django.shortcuts import redirect
from .forms import EventForm



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