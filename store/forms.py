from django import forms
from django.forms import Textarea, Select, RadioSelect, TextInput
from prompt_toolkit.widgets import RadioList

from .models import StoreProfile, QuestionComment, StoreGrade


class StoreProfileForm(forms.ModelForm):
    photo = forms.ImageField()
    def __init__(self, *args, **kwargs):
        super(StoreProfileForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = '가게 이름'
        self.fields['name'].widget.attrs.update({
            'class': 'form-control col-sm-10'
        })
        
        self.fields['photo'].label = '가게 사진'
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'style' : 'display: none;',
        })
        self.fields['comment'].label = '가게 소개'
        self.fields['comment'].widget.attrs.update({
            'class': 'form-control col-sm-10'
        })

    class Meta:
        model = StoreProfile
        fields = ['name','photo','comment']

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