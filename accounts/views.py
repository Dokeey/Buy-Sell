from django.shortcuts import render, redirect
from .forms import SginupForm

# Create your views here.


def sginup(request):
    if request.method == "POST":
        form = SginupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sginup')
    else:
        form = SginupForm()

    return render(request, 'accounts/sginup.html', {
        'form': form
    })