from django.contrib.auth.forms import UserCreationForm
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
from .models import Profile, phone_validate

User = get_user_model()



class SignupForm(UserCreationForm):

    phone = forms.CharField()
    nick_name = forms.CharField()
    address = forms.CharField(widget= forms.HiddenInput)
    account_num = forms.CharField()
    email = forms.EmailField()

    '''
    def clean_username(self):
        value = self.cleaned_data('username')
        if value:
            validate_email(value)
        return value
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].help_text = '이메일을 써야해요'
        self.fields['email'].label = '이메일'

        self.fields['username'].label = 'ID'

        self.fields['nick_name'].label = '닉네임'
        # self.fields['nick_name'].validators = [id_validate]

        self.fields['address'].label = '주소'

        self.fields['phone'].validators = [validate_integer, phone_validate]
        self.fields['phone'].help_text = "'-'를 제외한 숫자만 입력해주세요"
        self.fields['phone'].label = '연락처'

        self.fields['account_num'].validators = [validate_integer, MaxLengthValidator(20)]
        self.fields['account_num'].help_text = "'-'를 제외한 숫자만 입력해주세요"
        self.fields['account_num'].label = '계좌번호'

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone', 'nick_name', 'address', 'account_num', 'email')


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
        address = self.cleaned_data.get('address', None)
        nick_name = self.cleaned_data.get('nick_name', None)
        account_num = self.cleaned_data.get('account_num', None)

        Profile.objects.create(user=user, email=email,
                               phone=phone, address=address,
                               nick_name=nick_name, account_num=account_num)

        StoreProfile.objects.create(user=user, name=user.profile.nick_name + '의 가게')

class ProfileForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
    )
    class Meta:
        model = Profile
        fields = ['nick_name', 'email', 'phone', 'address', 'account_num', 'password']
        widgets = {
            'address': forms.HiddenInput,
        }