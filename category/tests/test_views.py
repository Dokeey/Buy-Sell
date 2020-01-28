
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
            Item.objects.create(user=seller, category=cls.cate, title='[중고]{}'.format(ctn), amount=100000+ctn)
            Item.objects.create(user=seller, category=cls.sub_cate, title='[중고]모니터{}'.format(ctn), amount=50000+ctn)


    def test_parent_category(self):
        response = self.client.get(reverse('category:category_item', kwargs={'pk': self.cate.id}), {'parent': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 10)
        self.assertFalse(response.context['parent_category'].exists())


    def test_sub_category(self):
        response = self.client.get(reverse('category:category_item', kwargs={'pk': self.sub_cate.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].count(), 10)
        self.assertQuerysetEqual(response.context['parent_category'], ['<Category: 전자제품>'])


    def test_ordering(self):
        response = self.client.get(reverse('category:category_item', kwargs={'pk': self.cate.id}), {'sort': 'hprice'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].first().amount, 100009)
        # self.assertEqual(response.context['items'].last().amount, 50000)



class SearchItemListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=seller, name='seller가게')

        cls.cate = Category.objects.create(name='전자제품')
        cls.sub_cate = Category.objects.create(name='모니터', parent=cls.cate)

        item_ctn = 10
        for ctn in range(item_ctn):
            Item.objects.create(user=seller, category=cls.cate, title='[중고]{}'.format(ctn), desc='설명{}'.format(ctn+1), amount=100000+ctn)
            Item.objects.create(user=seller, category=cls.sub_cate, title='[중고]모니터{}'.format(ctn), desc='sub설명{}'.format(ctn+1), amount=50000+ctn)


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


    def test_ordering(self):
        response = self.client.get(reverse('category:search_item'), {'query': '3 ', 'cate': self.sub_cate.id, 'sort': 'hprice'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['items'].first().amount, 50003)
        # self.assertEqual(response.context['items'].last().amount, 50000)



# 대용량 데이터베이스 검색 테스트
# class BigSearchTest(TestCase):
#
#     # 테스트 물품 생성, 주문자 생성, 주문서 생성
#     @classmethod
#     def setUpTestData(cls):
#         seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
#         StoreProfile.objects.create(user=seller, name='seller가게')
#
#         cate_ctn = 10
#         sub_ctn = 100
#         for cate in range(cate_ctn):
#             category = Category.objects.create(name='Parent_{}'.format(cate))
#             for sub in range(sub_ctn):
#                 Category.objects.create(name='{}_{}'.format(cate, sub), parent=category)
#
#         item_ctn = 10000000
#         ctn_by_cate = item_ctn//Category.objects.all().count()
#         item_list = []
#         for cate in Category.objects.all():
#             for ctn in range(ctn_by_cate):
#                 item = Item()
#                 item.user = seller
#                 item.category = cate
#                 item.title = '[중고]{}'.format(ctn)
#                 item.desc = '설명{}'.format(ctn+1)
#                 item.amount = 100000+ctn
#                 item_list.append(item)
#             Item.objects.bulk_create(item_list)
#             item_list = []
#
#
#     def test_query(self):
#         # self.assertEqual('hi', 'hi')
#         response = self.client.get(reverse('category:search_item'), {'query': ' 3'})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context['items'].count(), 4)
#         self.assertEqual(response.context['all_category'].count(), 2)