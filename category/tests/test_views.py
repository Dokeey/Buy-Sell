
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# 물품 모델 테스트
from category.models import Category
from trade.models import Item
from store.models import StoreProfile

User = get_user_model()

class CategoryItemListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=seller, name='seller가게')

        cls.cate = Category.objects.create(name='전자제품')
        cls.sub_cate = Category.objects.create(name='모니터', parent=cls.cate)

        item_ctn = 10
        for ctn in range(item_ctn):
            Item.objects.create(user=seller, category=cls.cate, title='[중고]{}'.format(ctn), amount=100000)
            Item.objects.create(user=seller, category=cls.sub_cate, title='[중고]모니터{}'.format(ctn), amount=50000)


    def test_parent_category(self):
        response = self.client.get(reverse('category:category_item', kwargs={'pk': self.cate.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 20)
        self.assertFalse(response.context['parent_category'].exists())


    def test_sub_category(self):
        response = self.client.get(reverse('category:category_item', kwargs={'pk': self.sub_cate.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 10)
        self.assertQuerysetEqual(response.context['parent_category'], ['<Category: 전자제품>'])



class SearchItemListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=seller, name='seller가게')

        cls.cate = Category.objects.create(name='전자제품')
        cls.sub_cate = Category.objects.create(name='모니터', parent=cls.cate)

        item_ctn = 10
        for ctn in range(item_ctn):
            Item.objects.create(user=seller, category=cls.cate, title='[중고]{}'.format(ctn), desc='설명{}'.format(ctn+1), amount=100000)
            Item.objects.create(user=seller, category=cls.sub_cate, title='[중고]모니터{}'.format(ctn), desc='sub설명{}'.format(ctn+1), amount=50000)


    def test_query(self):
        response = self.client.get(reverse('category:search_item'), {'query': ' 3'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 4)
        self.assertEqual(response.context['all_category'].count(), 2)


    def test_query_and_category(self):
        response = self.client.get(reverse('category:search_item'), {'query': '3 ', 'cate': self.sub_cate.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 2)
        self.assertEqual(response.context['all_category'].count(), 1)


    def test_none_query(self):
        response = self.client.get(reverse('category:search_item'), {'query': ''}, follow=True)
        self.assertEqual(list(response.context.get('messages'))[0].message, '검색어를 입력해주세요')
        self.assertRedirects(response, '/')