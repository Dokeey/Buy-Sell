from django import forms
from mptt.forms import TreeNodeChoiceField
from .models import CustomerAsk, CustomerCategory

class CustomerAskForm(forms.ModelForm):
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