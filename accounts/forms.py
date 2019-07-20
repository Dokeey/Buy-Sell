from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email, validate_integer, RegexValidator, \
    MaxLengthValidator  # 이메일 문법을 검사하는 클래스
from django import forms
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from store.models import StoreProfile
from .models import Profile

User = get_user_model()



class SignupForm(UserCreationForm):

    phone = forms.CharField()
    nick_name = forms.CharField()
    post_code = forms.CharField()
    address = forms.CharField()
    detail_address = forms.CharField()
    account_num = forms.CharField()
    email = forms.EmailField()
    CHOICE = (
        ("policy1", "(필수)Buy&Sell 이용약관 동의"),
        ("policy2", "(필수)개인정보 처리방침 동의"),
        ("policy3", "(선택)위치기반 서비스 이용약관 동의"),
        # ("policy3", "(선택)SNS, 이메일 마케팅 동의"),
    )
    policy_check = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CHOICE)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'ID'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': 'ID를 정해주세요',
        })
        self.fields['password1'].label = '비밀번호'
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '비밀번호를 입력해주세요',
        })
        self.fields['password2'].label = '비밀번호 확인'
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '비밀번호를 확인하겠습니다',
        })
        self.fields['nick_name'].label = '닉네임'
        self.fields['nick_name'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '닉네임을 정해주세요',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': 'ex) buynsell@naver.com',
        })
        self.fields['phone'].label = '연락처'
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })
        self.fields['post_code'].label = '우편번호'
        self.fields['post_code'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '우편 번호',
            'readonly': 'readonly',
            'onclick': 'Postcode()',
        })
        self.fields['address'].label = '주소'
        self.fields['address'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '주소',
            'readonly':'readonly',
            'onclick': 'Postcode()',
            'rows': 1,
            'cols': 80,
        })
        self.fields['detail_address'].label = '상세주소'
        self.fields['detail_address'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '상세 주소',
        })
        self.fields['account_num'].label = '계좌번호'
        self.fields['account_num'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })
        self.fields['policy_check'].label = '약관 동의'
        self.fields['policy_check'].widget.attrs.update({
            'required' : 'required',
        })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone', 'nick_name', 'post_code', 'address', 'detail_address', 'account_num', 'email','policy_check')


    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)

        if commit:
            user.is_active = False
            user.save()

            # 회원가입 인증 메일 발송
            send_mail(
                'hello,' + user.username,
                '',
                'buynsell',
                [user.email],
                fail_silently=False,
                html_message=render_to_string('accounts/user_activate_email.html', {
                    'user': user,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
                    'domain': 'localhost:8000',
                    'token': default_token_generator.make_token(user),
                }),
            )

        phone = self.cleaned_data.get('phone', None)
        email = self.cleaned_data.get('email', None)
        post_code = self.cleaned_data.get('post_code', None)
        address = self.cleaned_data.get('address', None)
        detail_address = self.cleaned_data.get('detail_address', None)
        nick_name = self.cleaned_data.get('nick_name', None)
        account_num = self.cleaned_data.get('account_num', None)

        Profile.objects.create(user=user, email=email,
                               phone=phone, address=address,
                               nick_name=nick_name, account_num=account_num,
                               post_code=post_code, detail_address=detail_address
                               )

        StoreProfile.objects.create(user=user, name=user.profile.nick_name + '의 가게')


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['nick_name'].label = '닉네임'
        self.fields['nick_name'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '닉네임을 정해주세요',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': 'ex) buynsell@naver.com',
        })
        self.fields['phone'].label = '연락처'
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })
        self.fields['post_code'].label = '우편번호'
        self.fields['post_code'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '우편 번호',
            'onclick': 'Postcode()',
        })
        self.fields['address'].label = '주소'
        self.fields['address'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '주소',
            'onclick': 'Postcode()',
            'rows': 1,
            'cols': 80,
        })
        self.fields['detail_address'].label = '상세주소'
        self.fields['detail_address'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '상세 주소',
        })
        self.fields['account_num'].label = '계좌번호'
        self.fields['account_num'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })

    class Meta:
        model = Profile
        fields = ['nick_name', 'email', 'phone', 'post_code', 'address', 'detail_address','account_num']


class AuthProfileForm(ProfileForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super(AuthProfileForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = '기존 비밀번호'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '기존 패스워드를 입력해주세요',
        })

    class Meta:
        model = ProfileForm.Meta.model
        fields = ProfileForm.Meta.fields + ['password']


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = '기존 비밀번호'
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '기존 패스워드를 입력해주세요',
        })
        self.fields['new_password1'].label = '새로운 비밀번호'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '새로운 패스워드를 입력해주세요',
        })
        self.fields['new_password2'].label = '비밀번호 확인'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '패스워드를 한번 더 입력해주세요',
        })


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'ID'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control input-sm chat-input',
            'placeholder': 'ID',
        })
        self.fields['password'].label = 'Password'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control input-sm chat-input',
            'placeholder': 'Password',
        })


class CheckPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super(CheckPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = '비밀번호'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '기존 패스워드를 입력해주세요',
        })

    class Meta:
        fields = ['password']