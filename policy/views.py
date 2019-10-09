from django.shortcuts import render, redirect
from django.views.generic import TemplateView

# Create your views here.

# def policy_service(request):
#     return render(request,'policy/service.html',{})

class PolicyServiceView(TemplateView):
    template_name = "policy/service.html"

# def policy_location(request):
#     return render(request,'policy/location.html',{})

# def policy_privacy(request):
#     return render(request,'policy/privacy.html',{})

class PolicyPrivacyView(TemplateView):
    template_name = "policy/privacy.html"