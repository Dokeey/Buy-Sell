from django.shortcuts import render, redirect
from .forms import SginupForm

# Create your views here.


def sginup(request):
    if request.method == "POST":
        form = SginupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # template에서 넘어온 인자들을 모두 합쳐 주소필드에 저장한다.
            return redirect('sginup')
    else:
        form = SginupForm()

    return render(request, 'accounts/sginup.html', {
        'form': form
    })