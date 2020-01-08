import json

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.files import File
from django.test import TestCase
from django.urls import reverse

# 물품 모델 테스트
from category.models import Category
from trade.models import Item
from store.models import StoreProfile
from mypage.models import WishList, Follow

User = get_user_model()

class WishListLVTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 구매자
        cls.order = get_user_model().objects.create_user(username='order', email='order@test.com', password='1234')
        StoreProfile.objects.create(user=cls.order, name='order가게')

        # 판매자
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')

        # 판매자 물품
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)

        cls.wish = WishList.objects.create(user=cls.order, item=cls.item)

    def test_view_url_name(self):
        response = self.client.get(reverse('mypage:wishlist'))
        self.assertRedirects(response, '/accounts/login/?next=/mypage/wishlist/')


    def test_login_view_url_name(self):
        self.client.login(username='order', password='1234')
        response = self.client.get(reverse('mypage:wishlist'))
        self.assertEqual(str(response.context['user']), 'order')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mypage/wishlist.html')
        self.assertEquals(response.context['wishlist_set'].count(), 1)
        self.assertQuerysetEqual(response.context['wishlist_set'], ['<WishList: [중고]닌텐도셋트>'])



class WishListTVTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 구매자
        cls.order = get_user_model().objects.create_user(username='order', email='order@test.com', password='1234')
        StoreProfile.objects.create(user=cls.order, name='order가게')

        # 판매자
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')

        # 판매자 물품
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)


    def test_view_url_name(self):
        response = self.client.get(reverse('mypage:wishlist_action', kwargs={'item_id': self.item.id}))
        self.assertRedirects(response, '/accounts/login/?next=/mypage/wishlist/{}/'.format(self.item.id))


    def test_wish_add(self):
        self.client.login(username='order', password='1234')
        response = self.client.get(reverse('mypage:wishlist_action', kwargs={'item_id': self.item.id}), follow=True)
        self.assertEqual(str(response.context['user']), 'order')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mypage/wishlist.html')
        self.assertEquals(list(response.context.get('messages'))[0].message, '찜 하셨습니다')
        self.assertEquals(response.context['wishlist_set'].count(), 1)
        self.assertQuerysetEqual(response.context['wishlist_set'], ['<WishList: [중고]닌텐도셋트>'])


    def test_seller_login_wish_add(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('mypage:wishlist_action', kwargs={'item_id': self.item.id}), follow=True)
        self.assertEqual(str(response.context['user']), 'seller')
        self.assertEquals(list(response.context.get('messages'))[0].message, '본인 물품은 찜할 수 없어요 ^^')
        self.assertEqual(response.status_code, 200)


    def test_wish_delete(self):
        WishList.objects.create(user=self.order, item=self.item)
        self.client.login(username='order', password='1234')
        response = self.client.get(reverse('mypage:wishlist_action', kwargs={'item_id': self.item.id}), follow=True)
        self.assertEqual(str(response.context['user']), 'order')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mypage/wishlist.html')
        self.assertEquals(list(response.context.get('messages'))[0].message, '찜을 삭제 하셨습니다')
        self.assertEquals(response.context['wishlist_set'].count(), 0)



class FollowLVTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 구매자
        cls.order = get_user_model().objects.create_user(username='order', email='order@test.com', password='1234')
        StoreProfile.objects.create(user=cls.order, name='order가게')

        # 판매자
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')

        # 판매자 물품
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)

        cls.wish = Follow.objects.create(user=cls.order, store=cls.seller.storeprofile)

    def test_view_url_name(self):
        response = self.client.get(reverse('mypage:follow'))
        self.assertRedirects(response, '/accounts/login/?next=/mypage/follow/')


    def test_login_view_url_name(self):
        self.client.login(username='order', password='1234')
        response = self.client.get(reverse('mypage:follow'))
        self.assertEqual(str(response.context['user']), 'order')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mypage/follow.html')
        self.assertEquals(response.context['follow_set'].count(), 1)
        self.assertQuerysetEqual(response.context['follow_set'], ['<Follow: seller가게>'])



class FollowTVTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 구매자
        cls.order = get_user_model().objects.create_user(username='order', email='order@test.com', password='1234')
        StoreProfile.objects.create(user=cls.order, name='order가게')

        # 판매자
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')

        # 판매자 물품
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)


    def test_view_url_name(self):
        response = self.client.get(reverse('mypage:follow_action', kwargs={'store_id': self.seller.storeprofile.id}))
        self.assertRedirects(response, '/accounts/login/?next=/mypage/follow/{}/'.format(self.seller.storeprofile.id))


    def test_follow_add(self):
        self.client.login(username='order', password='1234')
        response = self.client.get(reverse('mypage:follow_action', kwargs={'store_id': self.seller.storeprofile.id}), follow=True)
        self.assertEqual(str(response.context['user']), 'order')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mypage/follow.html')
        self.assertEquals(list(response.context.get('messages'))[0].message, '팔로우 하셨습니다')
        self.assertEquals(response.context['follow_set'].count(), 1)
        self.assertQuerysetEqual(response.context['follow_set'], ['<Follow: seller가게>'])


    def test_seller_login_follow_add(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('mypage:follow_action', kwargs={'store_id': self.seller.storeprofile.id}), follow=True)
        self.assertEqual(str(response.context['user']), 'seller')
        self.assertEquals(list(response.context.get('messages'))[0].message, '본인은 팔로우할 수 없어요 ^^')
        self.assertEqual(response.status_code, 200)


    def test_follow_delete(self):
        Follow.objects.create(user=self.order, store=self.seller.storeprofile)
        self.client.login(username='order', password='1234')
        response = self.client.get(reverse('mypage:follow_action', kwargs={'store_id': self.seller.storeprofile.id}), follow=True)
        self.assertEqual(str(response.context['user']), 'order')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mypage/follow.html')
        self.assertEquals(list(response.context.get('messages'))[0].message, '팔로우를 삭제 하셨습니다')
        self.assertEquals(response.context['follow_set'].count(), 0)