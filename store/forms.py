from django import forms

from .models import StoreProfile, QuestionComment


class StoreProfileForm(forms.ModelForm):
    class Meta:
        model = StoreProfile
        fields = ['name','photo','comment']


class StoreQuestionForm(forms.ModelForm):

    class Meta:
        model = QuestionComment
        fields = ['comment']
