from django import forms
from django.forms import Textarea, Select, RadioSelect, TextInput
from prompt_toolkit.widgets import RadioList

from .models import StoreProfile, QuestionComment, StoreGrade


class StoreProfileForm(forms.ModelForm):
    class Meta:
        model = StoreProfile
        fields = ['name','photo','comment']
        widgets = {
            'comment': Textarea(attrs={'class': 'form-control'}),
            'name': TextInput(attrs={'class': 'form-control'})
        }

class StoreQuestionForm(forms.ModelForm):

    class Meta:
        model = QuestionComment
        fields = ['comment']
        widgets = {
            'comment': Textarea(attrs={'class': 'form-control col-sm-10', 'rows': 3, 'cols': 50}),
        }

class StoreGradeForm(forms.ModelForm):
    class Meta:
        model = StoreGrade
        fields = ['grade_comment']
        widgets = {
            'grade_comment': Textarea(attrs={'class': 'form-control', 'rows': 5, 'cols': 50})
        }