from django import forms

from .models import StoreProfile, QuestionComment, StoreGrade


class StoreProfileForm(forms.ModelForm):
    class Meta:
        model = StoreProfile
        fields = ['name','photo','comment']


class StoreQuestionForm(forms.ModelForm):

    class Meta:
        model = QuestionComment
        fields = ['comment']

class StoreGradeForm(forms.ModelForm):
    class Meta:
        model = StoreGrade
        fields = ['grade_comment', 'rating']