from django import forms
from django_summernote import fields as summer_fields
from django_summernote.widgets import SummernoteWidget
from .models import CustomerAsk
from .models import CustomerAsk, CustomerCategory

class CustomerAskForm(forms.ModelForm):
    ask_post = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'placeholder':'문의 내용을 입력해 주세요. 사진 혹은 비디오를 이용하셔도 좋습니다.'}}))
    # ask_post = summer_fields.SummernoteTextFormField(error_messages={'required':(u'데이터를 입력해주세요'),})
    def __init__(self, *args, **kwargs):
        super(CustomerAskForm, self).__init__(*args, **kwargs)
        self.fields['ask_category'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'id' : 'ask_category'
            
        })
        self.fields['ask_title'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "문의 제목",
            'maxlength':"30",
            'id' : 'ask_title'
        })
    class Meta:
        model = CustomerAsk
        fields = ['ask_category', 'ask_title', 'ask_post']
        # widgets = {
        #     'ask_post': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
        # }