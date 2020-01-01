from django.contrib.auth import get_user_model
from django.test import TestCase


# 물품 모델 테스트
from trade.forms import PayForm

from category.models import Category
from trade.models import Item, Order


class PayFormTest(TestCase):

    # 테스트 물품 생성, 주문자 생성, 주문서 생성
    @classmethod
    def setUpTestData(cls):
        cate = Category.objects.create(name='전자제품')
        seller = get_user_model().objects.create(username='seller', email='seller@test.com')
        item = Item.objects.create(user=seller, category=cate, title='[중고]닌텐도셋트', amount=100000)
        order = get_user_model().objects.create(username='order', email='order@test.com')

        cls.trade = Order()
        cls.trade.user = order
        cls.trade.item = item
        cls.trade.username = '홍길동'
        cls.trade.phone = '0123456789'
        cls.trade.post_code = '123'
        cls.trade.address = '서울'
        cls.trade.detaul_address = '상암동'
        cls.trade.amount = 100000
        cls.trade.pay_choice = 'bank_trans'
        cls.trade.status = 'reserv'
        cls.trade.update()

    # 주문자 정보를 iamport 모듈에 넘겨주는 form 생성 확인
    def test_pay_form_fields_set(self):
        form = PayForm(instance=self.trade)
        self.assertTrue(form.as_iamport())