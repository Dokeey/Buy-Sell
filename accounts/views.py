from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from .forms import SginupForm

# Create your views here.


def signup(request):
    if request.method == "POST":
        form = SginupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # template에서 넘어온 인자들을 모두 합쳐 주소필드에 저장한다.
            return redirect('signup')
    else:
        form = SginupForm()

    return render(request, 'accounts/signup.html', {
        'form': form,
    })

signin = LoginView.as_view(template_name='accounts/login.html', success_url='accounts/signup.html')

signout = LogoutView.as_view()