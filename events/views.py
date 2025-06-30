from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

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