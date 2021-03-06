from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text, force_bytes
from django.views.generic import CreateView, TemplateView, UpdateView, FormView
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .supporter import send_mail
from .models import Profile
from .forms import SignupForm, AuthProfileForm, CustomPasswordChangeForm, CustomAuthenticationForm, CheckPasswordForm, \
    IdFindForm, CustomPasswordResetForm, CustomSetPasswordForm

User = get_user_model()


class SignupView(CreateView):
    model = User
    template_name = 'accounts/signup.html'
    form_class = SignupForm

    def get(self, request, *args, **kwargs):
        url = settings.LOGIN_REDIRECT_URL
        if request.user.is_authenticated:
            if url == request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, '회원님의 입력한 Email 주소로 인증 메일이 발송되었습니다. 메일을 확인하시고 로그인 해주세요!')
        return settings.LOGIN_URL

    def form_valid(self, form):
        self.object = form.save()

        # 회원가입 인증 메일 발송
        send_mail(
            '[Buy & Sell] {}님의 회원가입 인증메일 입니다.'.format(self.object.username),
            [self.object.email],
            html=render_to_string('accounts/user_activate_email.html', {
                'user': self.object,
                'uid': urlsafe_base64_encode(force_bytes(self.object.id)).decode('utf-8'),
                'domain': self.request.META['HTTP_HOST'],
                'token': default_token_generator.make_token(self.object),
            }),
        )
        return redirect(self.get_success_url())


class SigninView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.get_success_url() == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, user=self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    model = Profile
    template_name = 'accounts/profile_form.html'
    form_class = AuthProfileForm
    success_url = reverse_lazy('accounts:profile')

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = request.user.profile.id
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = get_object_or_404(Profile, user=self.request.user)
        if check_password(form.cleaned_data['password'], profile.user.password):
            return super().form_valid(form)
        else:
            errors = form._errors.setdefault("password", ErrorList())
            errors.append("패스워드를 확인해주세요 :(")
            return self.form_invalid(form)


@method_decorator(login_required, name='dispatch')
class PasswordChange(PasswordChangeView):
    template_name = 'accounts/pw_edit.html'
    success_url = reverse_lazy('accounts:profile')
    form_class = CustomPasswordChangeForm

    def form_valid(self, form):
        if form.cleaned_data['old_password'] == form.cleaned_data['new_password1']:
            errors = form._errors.setdefault("new_password1", ErrorList())
            errors.append("이전 비밀번호와 동일합니다.")
            return self.form_invalid(form)

        form.save()
        update_session_auth_hash(self.request, form.user)

        # 패스워드 변경 알림 메일 발송
        send_mail(
            '[Buy & Sell] {}님 방금 패스워드를 변경하셨습니다.'.format(self.request.user.username),
            [self.request.user.email],
            html=render_to_string('accounts/password_change_alert.html', {
                'user': self.request.user,
                'domain': self.request.META['HTTP_HOST'],
            }),
        )
        return redirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class UserDeleteView(FormView):
    model = User
    form_class = CheckPasswordForm
    template_name = 'accounts/user_delete.html'
    success_url = reverse_lazy('root')

    def form_valid(self, form):
        user = get_object_or_404(User, id=self.request.user.id)
        if check_password(form.cleaned_data['password'], user.password):
            self.request.user.delete()
            messages.info(self.request, '그동안 이용해주셔서 감사합니다.')
            logout(self.request)
            return redirect(self.success_url)
        else:
            messages.error(self.request, '패스워드를 확인해주세요 :(')
            return redirect('accounts:profile')


# 이메일 인증 활성화 뷰
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64.encode('utf-8')))
        current_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        messages.error(request, '메일 인증이 실패되었습니다.')
        return redirect('accounts:login')

    if default_token_generator.check_token(current_user, token):
        current_user.is_active = True
        current_user.save()

        messages.info(request, '메일 인증이 완료 되었습니다. 회원가입을 축하드립니다!')
        return redirect('accounts:login')

    messages.error(request, '메일 인증이 실패되었습니다.')
    return redirect('accounts:login')


class IdFindView(PasswordResetView):
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/id_find_form.html'
    email_template_name = 'accounts/user_id_find.html'
    form_class = IdFindForm
    subject = '[Buy & Sell] 아이디 찾기 결과입니다.'
    error_message = 'Email을 다시 한번 확인해주세요.'
    success_message = '아이디 찾기 메일을 발송했습니다.'

    def form_valid(self, form):
        context = {
            'subject': self.subject,
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'email_template_name': self.email_template_name,
            'request': self.request,
            'extra_email_context': self.extra_email_context,
        }
        flag = form.save(**context)
        if not flag:
            messages.error(self.request, self.error_message)
            return self.form_invalid(form)

        messages.info(self.request, self.success_message)
        return redirect(self.get_success_url())


# 비밀번호 찾기
class MyPasswordResetView(IdFindView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/user_password_reset.html'
    form_class = CustomPasswordResetForm
    subject = '[Buy & Sell] 비밀번호 찾기 결과입니다.'
    error_message = 'ID 혹은 Email을 다시 한번 확인해주세요.'
    success_message = '비밀번호 찾기 메일을 보냈습니다.'


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm

    def form_valid(self, form):
        messages.info(self.request, '비밀번호를 변경 하였습니다.')
        return super().form_valid(form)
