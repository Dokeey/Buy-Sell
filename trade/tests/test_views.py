import json
import os

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.files import File
from django.test import TestCase
from django.urls import reverse, reverse_lazy

# 물품 모델 테스트
from trade.forms import PayForm

from category.models import Category
from trade.models import Item, Order, ItemImage
from store.models import StoreProfile

User = get_user_model()

class ItemNewTest(TestCase):

    # 테스트 물품 생성, 주문자 생성, 주문서 생성
    @classmethod
    def setUpTestData(cls):

        seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=seller, name='seller가게')
        cls.cate = Category.objects.create(name='전자제품')


    # 주문자 정보를 iamport 모듈에 넘겨주는 form 생성 확인
    def test_view_url(self):
        response = self.client.get('/trade/item/new/')
        self.assertRedirects(response, '/accounts/login/?next=/trade/item/new/')


    def test_view_url_name(self):
        response = self.client.get(reverse_lazy('trade:item_new'))
        self.assertRedirects(response, '/accounts/login/?next=/trade/item/new/')


    def test_login_view_url_name(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse_lazy('trade:item_new'))
        self.assertEqual(str(response.context['user']), 'seller')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade/item_new.html')
        self.client.logout()


    def test_item_add(self):
        self.client.login(username='seller', password='1234')

        url = finders.find('profile/3.png')
        img = File(open(url, 'rb'))
        response = self.client.post(reverse('trade:item_new'), {
            'title': 'test item',
            'desc': 'test',
            'amount': 1000,
            'photo': img,
            'category': self.cate.id,
            'item_status': 's'
        })
        self.assertEquals(
            json.loads(str(response.content, encoding='utf-8'))['is_valid'],
            True
        )
        self.assertTrue(Item.objects.get(title='test item'))


    def test_item_add_fail(self):
        self.client.login(username='seller', password='1234')

        response = self.client.post(reverse('trade:item_new'), {
            'title': 'test item',
            'desc': 'test',
            'amount': 1000,
            'photo': '',
            'category': self.cate.id,
            'item_status': 't'
        })
        self.assertEquals(
            json.loads(str(response.content, encoding='utf-8'))['is_valid'],
            False
        )
        self.assertTrue(
            json.loads(str(response.content, encoding='utf-8'))['error']['photo'],
        )
        self.assertTrue(
            json.loads(str(response.content, encoding='utf-8'))['error']['item_status'],
        )
        # print(json.loads(str(response.content, encoding='utf-8')))
        self.assertFalse(Item.objects.filter(title='test item').exists())


    # 테스트 종료후 이미지 삭제
    def tearDown(self):
        try:
            imgs = Item.objects.get(title='test item').itemimage_set.all()
        except:
            return super().tearDown()

        for img in imgs:
            directory = os.path.dirname(img.photo.path)
            if os.path.isfile(img.photo.path):
                os.remove(img.photo.path)

            if len(os.listdir(directory)) == 0:
                os.rmdir(directory)

        return super().tearDown()