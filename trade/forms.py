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
    photo = forms.ImageField()
    category = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator=unichr(0x00A0) * 4)

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = '물품명'
        self.fields['title'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '무엇을 파세요?',
        })
        self.fields['desc'].label = '설명'
        self.fields['desc'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '물품에 대해 설명해주세요',
        })
        self.fields['amount'].label = '가격'
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '얼마에요?'
        })
        self.fields['photo'].label = '사진'
        self.fields['photo'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'multiple': 'multiple',
            'style' : 'display: none;',
        })
        self.fields['category'].label = '종류'
        self.fields['category'].widget.attrs.update({
            'class': 'form-control col-sm-10',
        })
        self.fields['item_status'].label = '상태'
        self.fields['item_status'].widget.attrs.update({
            'class': 'form-control col-sm-10',
        })

    class Meta:
        model = Item
        fields = ['title','desc','amount','photo','category', 'item_status']



class ItemUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemUpdateForm, self).__init__(*args, **kwargs)
        self.fields['pay_status'].label = '재고'
        self.fields['pay_status'].widget.attrs.update({
            'class': 'form-control col-sm-10',
        })

    class Meta:
        model = Item
        fields = ['pay_status']



class ItemCommentForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':50}))
    class Meta:
        model = ItemComment
        fields = ['message']

    def __init__(self, *args, **kwargs):
        super(ItemCommentForm, self).__init__(*args, **kwargs)
        self.fields['message'].label = '문의'
        self.fields['message'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '어떤게 궁금하세요?'
        })



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
            'buyer_email': self.instance.email,
            'buyer_name': self.instance.username,
            'buyer_tel': self.instance.phone,
            'buyer_postcode': self.instance.post_code,
            'buyer_addr': self.instance.address + self.instance.detail_address,
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



class OrderForm(forms.ModelForm):
    CHOICE = (
        ('import', '이니페이 카드결제'),
        ('bank_trans', '계좌이체'),
    )
    pay_choice = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICE)

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['pay_choice'].label = '거래방식'
        self.fields['pay_choice'].widget.attrs.update({
            # 'class': 'col-sm-10',
        })
        self.fields['username'].label = '수령인'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '실명을 입력해주세요',
        })
        self.fields['email'].label = '이메일'
        self.fields['email'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': 'ex) buynsell@naver.com',
        })
        self.fields['phone'].label = '연락처'
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': "'-'를 제외한 숫자로 입력해주세요",
        })
        self.fields['post_code'].label = '우편번호'
        self.fields['post_code'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '우편 번호',
            'onclick': 'Postcode()',
        })
        self.fields['address'].label = '주소'
        self.fields['address'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '주소',
            'onclick': 'Postcode()',
            'rows': 1,
            'cols': 80,
        })
        self.fields['detail_address'].label = '상세주소'
        self.fields['detail_address'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '상세 주소',
        })
        self.fields['requirement'].label = '배송시 요청사항'
        self.fields['requirement'].widget.attrs.update({
            'class': 'form-control col-sm-10',
            'placeholder': '요청사항을 기입하세요',
            'rows': 2,
            'cols': 80,
        })

    class Meta:
        model = Order
        fields = ['pay_choice', 'email', 'username', 'phone', 'post_code', 'address', 'detail_address', 'requirement']