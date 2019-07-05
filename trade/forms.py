import json

from django import forms

from category.models import Category
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from django.utils.six import unichr
from mptt.forms import TreeNodeChoiceField

from .models import Item, ItemComment, Order
from accounts.forms import ProfileForm


class ItemForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator=unichr(0x00A0) * 4)

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = 'Title'
        self.fields['title'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '물품명이 무엇인가요?'
        })
        self.fields['desc'].label = 'Desc'
        self.fields['desc'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '물품에 대해 설명해주세요'
        })
        self.fields['amount'].label = 'Amount'
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '가격이 얼마에요?'
        })
        self.fields['photo'].label = 'Photo'
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control col-sm-10',
        })
        self.fields['category'].label = 'Category'
        self.fields['category'].widget.attrs.update({
            'class': 'form-control col-sm-10',
        })
        self.fields['item_status'].label = 'Status'
        self.fields['item_status'].widget.attrs.update({
            'class': 'form-control col-sm-10',
        })

    class Meta:
        model = Item
        fields = ['title','desc','amount','photo','category', 'item_status']


class ItemUpdateForm(ItemForm):
    class Meta:
        model = ItemForm.Meta.model
        fields = ItemForm.Meta.fields + ['pay_status']


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
            'buyer_email': self.instance.buyer_email,
            'buyer_name': self.instance.buyer_name,
            'buyer_tel': self.instance.buyer_tel,
            'buyer_addr': self.instance.buyer_addr,
            'buyer_postcode': self.instance.buyer_postcode,
        }
        return hidden_fields + render_to_string('trade/_iamport.html', {
            'json_fields': mark_safe(json.dumps(fields, ensure_ascii=False)),
            'iamport_shop_id': settings.IAMPORT_SHOP_ID, # FIXME: 각자의 상점 아이디로 변경 가능
        })

    def save(self):
        order = super().save(commit=False)
        # order.status = 'paid' # FIXME: 아임포트 API를 통한 확인 후에 변경을 해야만 합니다.
        # order.save()
        order.update()
        return order

class OrderForm(ProfileForm):
    CHOICE = (
        ('import', '이니페이 카드결제'),
        ('bank_trans', '계좌이체'),
    )
    pay_choice = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICE)
    class Meta:
        model = ProfileForm.Meta.model
        fields = ProfileForm.Meta.fields + ['pay_choice']
        widgets = ProfileForm.Meta.widgets