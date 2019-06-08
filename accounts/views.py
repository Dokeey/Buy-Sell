from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, \
    PasswordResetConfirmView
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from .models import Profile
from .forms import SignupForm, AuthProfileForm, CheckUserForm

User = get_user_model()


def signup(request):
    get_success_url = settings.LOGIN_REDIRECT_URL
    if request.user.is_authenticated:
        redirect_to = get_success_url
        if redirect_to == request.path:
            raise ValueError(
                "Redirection loop for authenticated user detected. Check that "
                "your LOGIN_REDIRECT_URL doesn't point to a login page."
            )
        return HttpResponseRedirect(redirect_to)

    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            # 메일 인증
            # current_site = get_current_site(self.request)

            # template에서 넘어온 인자들을 모두 합쳐 주소필드에 저장한다.
            return redirect('accounts:login')
    else:
        form = SignupForm()

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
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'accounts/profile.html',{
        'profile': profile,
    })


def check_user(fn):
    def wrapper(*args, **kwargs):
        request = args[0]
        profile = get_object_or_404(Profile, user=request.user)
        if request.method == "POST":
            form = CheckUserForm(request.POST)
            if form.is_valid():
                if check_password(form.cleaned_data['password'], profile.user.password):
                    return True
                else:
                    messages.error(request, '패스워드를 확인해주세요 :(')
        else:
            form = CheckUserForm

        return render(request, 'accounts/check_user.html', {
            'form': form
        })
    return wrapper

@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = AuthProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if check_password(request.POST['password'], profile.user.password):
                form.save()
                return redirect('accounts:profile')
            else:
                messages.error(request, '패스워드를 확인해주세요 :(')
    else:
        form = AuthProfileForm(instance=profile)

    return render(request, 'accounts/profile_form.html',{
        'form': form
    })


@method_decorator(login_required, name='dispatch')
class PasswordChange(PasswordChangeView):
    template_name = 'accounts/pw_edit.html'
    success_url = reverse_lazy('accounts:profile')

pw_edit = PasswordChange.as_view()


def withdrawal(request):
    request.user.delete()
    return redirect('root')


# 이메일 인증 활성화 뷰
def activate(request, uidb64, token):
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

#비밀번호 찾기
class MyPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/password_reset_form.html'
    email_template_name='accounts/user_password_reset.html'
    html_email_template_name='accounts/user_password_reset.html'

    def form_valid(self, form):
        messages.info(self.request, '암호 메일을 보냈습니다.')
        return super().form_valid(form)

class MyPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/password_reset_confirm.html'

    def form_valid(self, form):
        messages.info(self.request, '암호를 변경 하였습니다.')
        return super().form_valid(form)

class IdFindView(PasswordResetView):

    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/password_reset_form.html'
    subject_template_name = 'accounts/user_id_find_name.html'
    email_template_name = 'accounts/user_id_find.html'
    html_email_template_name = 'accounts/user_id_find.html'

    def form_valid(self, form):
        messages.info(self.request, '아이디 확인 메일을 보냈습니다.')
        return super().form_valid(form)