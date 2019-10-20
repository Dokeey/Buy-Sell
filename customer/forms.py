from django import forms
from django_summernote import fields as summer_fields

from .models import CustomerAsk


class CustomerAskForm(forms.ModelForm):
    ask_post = summer_fields.SummernoteTextFormField(error_messages={'required': (u'질문 사항을 입력해주세요'), })
    class Meta:
        model = CustomerAsk
        fields = ['ask_category', 'ask_title', 'ask_post']