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
    # CHOICES = []
    # for cate in Category.objects.all():
    #     category = []
    #     category.append(cate)
    #     sub_category_group = []
    #     for subcate in SubCategory.objects.filter(category=cate):
    #         sub_category = []
    #         sub_category.append(subcate.id)
    #         sub_category.append(subcate)
    #         sub_category_group.append(sub_category)
    #
    #     category.append(sub_category_group)
    #     CHOICES.append(category)

    category = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator=unichr(0x00A0) * 4)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].label = '카테고리'

    class Meta:
        model = Item
        fields = ['title','desc','amount','photo','category', 'item_status']


class ItemUpdateForm(ItemForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_tmp'].initial = self.instance.category.id

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