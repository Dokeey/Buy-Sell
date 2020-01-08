
from django.contrib.auth import get_user_model
from django.test import TestCase

from category.models import Category
from trade.models import Item
from mypage.models import WishList, Follow
from store.models import StoreProfile


# 물품 모델 테스트
class WishListTest(TestCase):
    # 유저, 카테고리를 생성 후 테스트 물품을 생성
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        seller = get_user_model().objects.create(username='test', email='test@test.com')
        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')

        cate = Category.objects.create(name='testcategory')

        item = Item.objects.create(user=seller, category=cate, title='testitem', amount=1000)
        cls.ITEM_ID = item.id

        cls.wish = WishList.objects.create(user=other_user, item=item)


    # 물품의 label이 제대로 나오는지 테스트
    def test_user_label(self):
        wish = WishList.objects.get(id=self.wish.id)
        field_label = wish._meta.get_field('user').verbose_name
        self.assertEquals(field_label, '사용자')


    # 물품의 label이 제대로 나오는지 테스트
    def test_item_label(self):
        wish = WishList.objects.get(id=self.wish.id)
        field_label = wish._meta.get_field('item').verbose_name
        self.assertEquals(field_label, '물품')


    # 물품 verbose name 테스트
    def test_wishlist_model_verbose_name(self):
        wish = WishList.objects.get(id=self.wish.id)
        verbose_name = wish._meta.verbose_name
        self.assertEquals(verbose_name, '찜 목록')



# 물품 모델 테스트
class FollowTest(TestCase):
    # 유저, 카테고리를 생성 후 테스트 물품을 생성
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        seller = get_user_model().objects.create(username='test', email='test@test.com')
        seller_store = StoreProfile.objects.create(user=seller, name='seller가게')

        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')
        StoreProfile.objects.create(user=other_user, name='other가게')

        cls.follow = Follow.objects.create(user=other_user, store=seller_store)


    # 물품의 label이 제대로 나오는지 테스트
    def test_user_label(self):
        follow = Follow.objects.get(id=self.follow.id)
        field_label = follow._meta.get_field('user').verbose_name
        self.assertEquals(field_label, '사용자')


    # 물품의 label이 제대로 나오는지 테스트
    def test_store_label(self):
        follow = Follow.objects.get(id=self.follow.id)
        field_label = follow._meta.get_field('store').verbose_name
        self.assertEquals(field_label, '가게')


    # 물품 verbose name 테스트
    def test_follow_model_verbose_name(self):
        follow = Follow.objects.get(id=self.follow.id)
        verbose_name = follow._meta.verbose_name
        self.assertEquals(verbose_name, '팔로우')
