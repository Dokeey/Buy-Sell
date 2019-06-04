import json

from django import forms

from category.models import Category, SubCategory
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import smart_text

from .models import Item, ItemComment, Order

from django.utils.safestring import mark_safe


class ItemForm(forms.ModelForm):
    CHOICES = []
    for cate in Category.objects.all():
        category = []
        category.append(cate)
        sub_category_group = []
        for subcate in SubCategory.objects.filter(category=cate):
            sub_category = []
            sub_category.append(subcate.id)
            sub_category.append(subcate)
            sub_category_group.append(sub_category)

        category.append(sub_category_group)
        CHOICES.append(category)

    category_tmp = forms.ChoiceField(choices=CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_tmp'].label = '카테고리'

        try:
            if kwargs['instance']:
                self.fields['category_tmp'].initial = self.instance.category.id
        except:
            pass
    class Meta:
        model = Item
        fields = ['title','desc','amount','photo','category_tmp', 'status','is_public']


class ItemCommentForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':50}))
    class Meta:
        model = ItemComment
        fields = ['message']


class PayForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['imp_uid',]
        widgets = {
            'imp_uid': forms.HiddenInput,
        }

    def as_iamport(self):
        # 본 Form의 Hidden 필드 위젯
        hidden_fields = mark_safe(''.join(smart_text(field) for field in self.hidden_fields()))
        # IMP.request_pay의 인자로 넘길 인자 목록
        fields = {
            'merchant_uid': str(self.instance.merchant_uid),
            'name': self.instance.name,
            'amount': self.instance.amount,
        }
        return hidden_fields + render_to_string('shop/_iamport.html', {
            'json_fields': mark_safe(json.dumps(fields, ensure_ascii=False)),
            'iamport_shop_id': settings.IAMPORT_SHOP_ID, # FIXME: 각자의 상점 아이디로 변경 가능
        })
