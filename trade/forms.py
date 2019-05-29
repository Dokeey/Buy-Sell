from django import forms

from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title','desc','amount','photo','category','sub_category','status','is_public']