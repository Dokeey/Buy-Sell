from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import validate_email, validate_integer   # 이메일 문법을 검사하는 클래스
from django import forms
from .models import User



class SginupForm(UserCreationForm):

    phone = forms.IntegerField()
    nic_name = forms.CharField()
    address = forms.CharField()
    account_num = forms.IntegerField()

    '''
    def clean_username(self):
        value = self.cleaned_data('username')
        if value:
            validate_email(value)
        return value
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['username'].validators = [validate_email]
        #self.fields['username'].help_text = '이메일을 써야해요'
        self.fields['username'].label = 'ID'

        self.fields['nic_name'].label = '닉네임'

        self.fields['address'].label = '주소'

        self.fields['phone'].validators = [validate_integer]
        self.fields['phone'].help_text = "'-'를 제외한 숫자만 입력해주세요"
        self.fields['phone'].label = '연락처'

        self.fields['account_num'].validators = [validate_integer]
        self.fields['account_num'].help_text = "'-'를 제외한 숫자만 입력해주세요"
        self.fields['account_num'].label = '계좌번호'

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields