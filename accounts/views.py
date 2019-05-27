from django import views
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import UpdateView, TemplateView

from .forms import SginupForm, ProfileForm

# Create your views here.
User = get_user_model()


def signup(request):
    if request.method == "POST":
        form = SginupForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            # 메일 인증
            # current_site = get_current_site(self.request)

            # template에서 넘어온 인자들을 모두 합쳐 주소필드에 저장한다.
            return redirect('accounts:signup')
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


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit(request):
    profile = get_object_or_404(User, pk=request.user.pk)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_form.html',{
        'form': form
    })


@method_decorator(login_required, name='dispatch')
class PasswordChange(PasswordChangeView):
    template_name = 'accounts/pw_edit.html'
    success_url = reverse_lazy('accounts:profile')

pw_edit = PasswordChange.as_view()



#이메일 인증 활성화 뷰
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64.encode('utf-8')))
        current_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        raise None

    if default_token_generator.check_token(current_user, token):
        current_user.is_active = True
        current_user.save()

        messages.info(request, '메일 인증이 완료 되었습니다.')
        return redirect('accounts:login')

    messages.error(request, '메일 인증이 실패되었습니다.')
    return redirect('accounts:login')



