from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, "home.html")

def contact(request):
    print("Contact view accessed")
    return HttpResponse("Welcome to the contact section")

def aboutUs(request):
    print("AboutUs view accessed")
    return HttpResponse("About us")

def events(request):
    return render(request, "events.html")

def show_event(request):
    return render(request, "show_event.html")