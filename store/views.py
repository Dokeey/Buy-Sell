from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import StoreProfile

@login_required
def store_profile(request):
    model = StoreProfile
    return render(request, 'store/storeprofile.html')



