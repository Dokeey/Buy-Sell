from django import forms

from .models import StoreProfile


class StoreProfileForm(forms.ModelForm):
    class Meta:
        model = StoreProfile
        fields = ['name','photo','comment']
