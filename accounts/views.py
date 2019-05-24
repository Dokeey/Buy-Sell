from django.shortcuts import render

# Create your views here.


def sginup(request):
    return render(request, 'accounts/sginup.html')