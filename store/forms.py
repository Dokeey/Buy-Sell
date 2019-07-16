from django import forms
from django.forms import Textarea, Select, RadioSelect
from prompt_toolkit.widgets import RadioList

from .models import StoreProfile, QuestionComment, StoreGrade


class StoreProfileForm(forms.ModelForm):
    class Meta:
        model = StoreProfile
        fields = ['name','photo','comment']


class StoreQuestionForm(forms.ModelForm):

    class Meta:
        model = QuestionComment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'class': 'bubble'}),
        }

class StoreGradeForm(forms.ModelForm):
    class Meta:
        model = StoreGrade
        fields = ['grade_comment']
        widgets = {
            'grade_comment': Textarea(attrs={'class': 'form-control'})
        }