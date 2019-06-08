from django import forms

from .models import CustomerAsk


class CustomerAskForm(forms.ModelForm):
    class Meta:
        model = CustomerAsk
        fields = ['ask_category', 'ask_title', 'ask_post']