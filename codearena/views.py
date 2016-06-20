from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    user = request.user
    return render(request, 'home.html', {'user':user})
    
def calendar(request):
    user = request.user
    return render(request, 'calendar.html', {'user':user})
    
def denied(request):
    user = request.user
    return render(request, 'denied.html', {'user':user})
