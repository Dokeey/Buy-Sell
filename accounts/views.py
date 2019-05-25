from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator

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


class SigninView(LoginView):
    template_name = 'accounts/login.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

signout = LogoutView.as_view()