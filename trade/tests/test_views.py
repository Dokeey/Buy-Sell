import json
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.files import File
from django.test import TestCase
from django.urls import reverse

# 물품 모델 테스트
from trade.forms import PayForm
from accounts.models import Profile
from category.models import Category
from trade.models import Item, Order, ItemImage, ItemComment
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
        response = self.client.get(reverse('trade:item_new'))
        self.assertRedirects(response, '/accounts/login/?next=/trade/item/new/')


    def test_login_view_url_name(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('trade:item_new'))
        self.assertEqual(str(response.context['user']), 'seller')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade/item_new.html')


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

        if not settings.USE_AWS:
            for img in imgs:
                directory = os.path.dirname(img.photo.path)
                if os.path.isfile(img.photo.path):
                    os.remove(img.photo.path)

                if len(os.listdir(directory)) == 0:
                    os.rmdir(directory)

        return super().tearDown()



class ItemUpdateTest(TestCase):
    # 테스트 물품 생성, 주문자 생성, 주문서 생성
    @classmethod
    def setUpTestData(cls):

        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)


    def test_view_url_name(self):
        response = self.client.get(reverse('trade:item_update', kwargs={'pk': self.item.id}))
        self.assertRedirects(response, '/accounts/login/?next=/trade/item/update/{}/'.format(self.item.id))


    def test_other_login_view_url_name(self):
        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')
        StoreProfile.objects.create(user=other_user, name='other가게')

        self.client.login(username='other', password='1234')
        response = self.client.get(reverse('trade:item_update', kwargs={'pk': self.item.id}), follow=True)
        self.assertEquals(list(response.context.get('messages'))[0].message, '잘못된 접근 입니다.')
        self.assertRedirects(response, '/')


    def test_login_view_url_name(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('trade:item_update', kwargs={'pk': self.item.id}))
        self.assertEqual(str(response.context['user']), 'seller')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade/item_update.html')


    def test_item_update(self):
        self.client.login(username='seller', password='1234')
        id = self.item.id
        response = self.client.post(reverse('trade:item_update', kwargs={'pk': id}), {
            'pay_status': 'sale_complete'
        })

        self.assertEquals(
            json.loads(str(response.content, encoding='utf-8'))['pay_status'],
            '판매완료'
        )
        self.assertEquals(Item.objects.get(id=id).pay_status, 'sale_complete')


    def test_item_update_fail(self):
        self.client.login(username='seller', password='1234')
        id = self.item.id
        response = self.client.post(reverse('trade:item_update', kwargs={'pk': id}), {
            'pay_status': 'hacked'
        })

        self.assertFormError(
            response, 'form', 'pay_status',
            '올바르게 선택해 주세요. hacked 이/가 선택가능항목에 없습니다.'
        )
        self.assertEquals(Item.objects.get(id=id).pay_status, 'ready')



class ItemDetailTest(TestCase):
    # 테스트 물품 생성, 주문자 생성, 주문서 생성
    @classmethod
    def setUpTestData(cls):
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)
        cls.cmt = ItemComment.objects.create(user=cls.seller, item=cls.item, message='im seller')


    def test_view_url_name(self):
        Item.objects.create(user=self.seller, category=self.cate, title='[중고]맥북', amount=100000, pay_status='sale_complete')
        Item.objects.create(user=self.seller, category=self.cate, title='[중고]아이폰', amount=100000)

        response = self.client.get(reverse('trade:item_detail', kwargs={'pk': self.item.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trade/item_detail.html')

        self.assertTrue('wish_ctn' in response.context)
        self.assertTrue('follow_ctn' in response.context)
        self.assertTrue('items' in response.context)
        self.assertQuerysetEqual(response.context['items'], ['<Item: [중고]아이폰>'])
        self.assertTrue('items_ctn' in response.context)
        self.assertEquals(str(response.context['items_ctn']), '1')
        self.assertTrue('kakao_key' in response.context)
        self.assertTrue('facebook_key' in response.context)


    def test_comment_add_not_login(self):
        response = self.client.post(reverse('trade:item_detail', kwargs={'pk': self.item.id}), {
            'message': 'hello django test'
        })
        self.assertRedirects(response, '/accounts/login/?next=/trade/item/detail/{}/'.format(self.item.id))


    def test_comment_add(self):
        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')
        StoreProfile.objects.create(user=other_user, name='other가게')

        self.client.login(username='other', password='1234')
        response = self.client.post(reverse('trade:item_detail', kwargs={'pk': self.item.id}), {
            'message': 'hello django test'
        })
        self.assertTrue(ItemComment.objects.filter(item=self.item, user=other_user).exists())
        self.assertIsNone(ItemComment.objects.get(item=self.item, user=other_user).parent)


    def test_reply_comment_add(self):
        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')
        StoreProfile.objects.create(user=other_user, name='other가게')

        self.client.login(username='other', password='1234')
        response = self.client.post(reverse('trade:item_detail', kwargs={'pk': self.item.id}), {
            'message': 'hello django test',
            'parent_id': self.cmt.id
        })
        self.assertTrue(ItemComment.objects.filter(item=self.item, user=other_user).exists())
        self.assertEquals(self.cmt, ItemComment.objects.get(item=self.item, user=other_user).parent)


    def test_comment_pagination(self):
        cmt_cnt = 8
        for cnt in range(cmt_cnt):
            ItemComment.objects.create(user=self.seller, item=self.item, message='hi')

        response = self.client.get(reverse('trade:item_detail', kwargs={'pk': self.item.id}), {'page': 2})

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['comments']), 4)



class ItemDeleteTest(TestCase):
    # 테스트 물품 생성, 주문자 생성, 주문서 생성
    @classmethod
    def setUpTestData(cls):
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)
        cls.cmt = ItemComment.objects.create(user=cls.seller, item=cls.item, message='im seller')


    def test_view_url_name(self):
        response = self.client.get(reverse('trade:item_delete', kwargs={'pk': self.item.id}))
        self.assertRedirects(response, '/accounts/login/?next=/trade/item/delete/{}/'.format(self.item.id))


    def test_view_url_name_other_login(self):
        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')
        StoreProfile.objects.create(user=other_user, name='other가게')

        self.client.login(username='other', password='1234')
        response = self.client.get(reverse('trade:item_delete', kwargs={'pk': self.item.id}), follow=True)
        self.assertEquals(list(response.context.get('messages'))[0].message, '잘못된 접근 입니다.')
        self.assertRedirects(response, '/')


    def test_get_item_delete(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('trade:item_delete', kwargs={'pk': self.item.id}))
        self.assertEquals(response.status_code, 200)


    def test_post_item_delete(self):
        self.client.login(username='seller', password='1234')
        response = self.client.post(reverse('trade:item_delete', kwargs={'pk': self.item.id}))
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())
        self.assertFalse(ItemComment.objects.filter(item=self.item.id).exists())
        self.assertRedirects(response, reverse('store:store_sell_list', kwargs={'pk': self.seller.storeprofile.id}))



class CommentUpdateTest(TestCase):
    # 테스트 물품 생성, 주문자 생성, 주문서 생성
    @classmethod
    def setUpTestData(cls):
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)
        cls.cmt = ItemComment.objects.create(user=cls.seller, item=cls.item, message='im seller')


    def test_view_url_name(self):
        response = self.client.get(reverse('trade:comment_update', kwargs={'pk': self.item.id, 'cid': self.cmt.id}))
        self.assertRedirects(response, '/accounts/login/?next=/trade/comment/update/{}/{}/'.format(self.item.id, self.cmt.id))


    def test_view_url_name_other_login(self):
        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')
        StoreProfile.objects.create(user=other_user, name='other가게')

        self.client.login(username='other', password='1234')
        response = self.client.get(reverse('trade:comment_update', kwargs={'pk': self.item.id, 'cid': self.cmt.id}), follow=True)
        self.assertEquals(list(response.context.get('messages'))[0].message, '잘못된 접근 입니다.')
        self.assertRedirects(response, reverse('trade:item_detail', kwargs={'pk': self.item.id}))


    def test_get_comment_update(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('trade:comment_update', kwargs={'pk': self.item.id, 'cid': self.cmt.id}))
        self.assertEquals(response.status_code, 200)


    def test_post_comment_update(self):
        self.client.login(username='seller', password='1234')
        response = self.client.post(reverse('trade:comment_update', kwargs={'pk': self.item.id, 'cid': self.cmt.id}), {
            'message': 'hello django test'
        })

        self.assertEquals(ItemComment.objects.get(id=self.cmt.id).message, 'hello django test')
        self.assertEquals(json.loads(str(response.content, encoding='utf-8'))['msg'], 'hello django test')



class CommentDeleteTest(TestCase):
    # 테스트 물품 생성, 주문자 생성, 주문서 생성
    @classmethod
    def setUpTestData(cls):
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)
        cls.cmt = ItemComment.objects.create(user=cls.seller, item=cls.item, message='im seller')


    def test_view_url_name(self):
        response = self.client.get(reverse('trade:comment_delete', kwargs={'pk': self.item.id, 'cid': self.cmt.id}))
        self.assertRedirects(response, '/accounts/login/?next=/trade/comment/delete/{}/{}/'.format(self.item.id, self.cmt.id))


    def test_view_url_name_other_login(self):
        other_user = get_user_model().objects.create_user(username='other', email='other@test.com', password='1234')
        StoreProfile.objects.create(user=other_user, name='other가게')

        self.client.login(username='other', password='1234')
        response = self.client.get(reverse('trade:comment_delete', kwargs={'pk': self.item.id, 'cid': self.cmt.id}), follow=True)
        self.assertEquals(list(response.context.get('messages'))[0].message, '잘못된 접근 입니다.')
        self.assertRedirects(response, reverse('trade:item_detail', kwargs={'pk': self.item.id}))


    def test_get_item_delete(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('trade:comment_delete', kwargs={'pk': self.item.id, 'cid': self.cmt.id}))
        self.assertEquals(response.status_code, 200)


    def test_post_item_delete(self):
        self.client.login(username='seller', password='1234')
        response = self.client.post(reverse('trade:comment_delete', kwargs={'pk': self.item.id, 'cid': self.cmt.id}))
        self.assertTrue(Item.objects.filter(id=self.item.id).exists())
        self.assertFalse(ItemComment.objects.filter(id=self.cmt.id).exists())
        self.assertEquals(response.status_code, 200)



class OrderNewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 구매자
        cls.order = get_user_model().objects.create_user(username='order', email='order@test.com', password='1234')
        StoreProfile.objects.create(user=cls.order, name='order가게')
        Profile.objects.create(
            user=cls.order,
            phone='0123456789',
            post_code='111',
            address='상암동',
            detail_address='101호',
            account_num='123'
        )
        # 판매자
        cls.seller = get_user_model().objects.create_user(username='seller', email='seller@test.com', password='1234')
        StoreProfile.objects.create(user=cls.seller, name='seller가게')
        Profile.objects.create(
            user=cls.seller,
            phone='0122222222',
            post_code='13321',
            address='둔촌동',
            detail_address='301호',
            account_num='321'
        )
        # 판매자 물품
        cls.cate = Category.objects.create(name='전자제품')
        cls.item = Item.objects.create(user=cls.seller, category=cls.cate, title='[중고]닌텐도셋트', amount=100000)

    # 비회원 접근
    def test_view_url_name(self):
        response = self.client.get(reverse('trade:order_new', kwargs={'item_id': self.item.id}))
        self.assertRedirects(response, '/accounts/login/?next=/trade/order/new/{}/'.format(self.item.id))

    # 본인 물품 접근
    def test_get_seller_login(self):
        self.client.login(username='seller', password='1234')
        response = self.client.get(reverse('trade:order_new', kwargs={'item_id': self.item.id}), follow=True)
        self.assertEquals(list(response.context.get('messages'))[0].message, '자신의 물품은 구매할수 없습니다.')
        self.assertEquals(response.status_code, 200)

    # 예약 or 판매완료 물품 접근
    def test_get_sells_item(self):
        self.client.login(username='order', password='1234')
        item = Item.objects.create(user=self.seller, category=self.cate, title='[중고]맥북', amount=100000, pay_status='reservation')
        response = self.client.get(reverse('trade:order_new', kwargs={'item_id': item.id}), follow=True)
        self.assertEquals(list(response.context.get('messages'))[0].message, '이미 예약이 되었거나 판매완료 상품입니다.')
        self.assertEquals(response.status_code, 200)

    # 회원 접근 (정상)
    def test_get_order_item(self):
        self.client.login(username='order', password='1234')
        response = self.client.get(reverse('trade:order_new', kwargs={'item_id': self.item.id}))
        self.assertEquals(response.status_code, 200)


    def test_post_order_item_import(self):
        self.client.login(username='order', password='1234')
        response = self.client.post(reverse('trade:order_new', kwargs={'item_id': self.item.id}), {
            'username': '홍길동',
            'phone': '0123456789',
            'post_code': '111',
            'address': '상암동',
            'detail_address': '101호',
            'email': 'order@aaa.com',
            'pay_choice': 'import'
        })

        order = Order.objects.get(item=self.item, user=self.order)
        self.assertTrue('/trade/order/{}/pay/'.format(self.item.id) in response['Location'])
        self.assertRedirects(response, '/trade/order/{}/pay/{}/'.format(self.item.id, str(order.merchant_uid)))


    def test_post_order_item_banktrans(self):
        self.client.login(username='order', password='1234')
        response = self.client.post(reverse('trade:order_new', kwargs={'item_id': self.item.id}), {
            'username': '홍길동',
            'phone': '0123456789',
            'post_code': '111',
            'address': '상암동',
            'detail_address': '101호',
            'email': 'order@aaa.com',
            'pay_choice': 'bank_trans'
        }, HTTP_HOST='example.com')

        order = Order.objects.get(item=self.item, user=self.order)
        self.assertRedirects(response, '/trade/info/{}/'.format(order.id))
        self.assertEquals(order.status, 'reserv')
        self.assertEquals(order.is_active, False)
