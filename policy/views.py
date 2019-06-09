from django.shortcuts import render, redirect


# Create your views here.

def policy_service(request):
    return render(request,'policy/service.html',{})

def policy_location(request):
    return render(request,'policy/location.html',{})

def policy_privacy(request):
    return render(request,'policy/privacy.html',{})