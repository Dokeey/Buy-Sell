from django import forms
from django_summernote import fields as summer_fields

from .models import CustomerAsk
from .models import CustomerAsk, CustomerCategory

class CustomerAskForm(forms.ModelForm):
    ask_post = summer_fields.SummernoteTextFormField(error_messages={'required': (u'질문 사항을 입력해주세요'), })
    def __init__(self, *args, **kwargs):
        super(CustomerAskForm, self).__init__(*args, **kwargs)
        self.fields['ask_category'].widget.attrs.update({
            'class': 'form-control col-sm-10'
            
        })
        self.fields['ask_title'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "문의 제목",
            'maxlength':"30"
        })
        self.fields['ask_post'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "문의 내용"
        })
    class Meta:
        model = CustomerAsk
        fields = ['ask_category', 'ask_title', 'ask_post']