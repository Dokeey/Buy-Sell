import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.files import File
from django.test import TestCase

from category.models import Category
from trade.models import Item, ItemImage, ItemComment, Order


# 물품 모델 테스트
class ItemModelTest(TestCase):

    # 유저, 카테고리를 생성 후 테스트 물품을 생성
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = get_user_model().objects.create(username='test', email='test@test.com')
        cate = Category.objects.create(name='testcategory')

        item = Item.objects.create(user=user, category=cate, title='testitem', amount=1000)
        cls.ITEM_ID = item.id

    # 물품의 label이 제대로 나오는지 테스트
    def test_title_label(self):
        item = Item.objects.get(id=self.ITEM_ID)
        field_label = item._meta.get_field('title').verbose_name
        self.assertEquals(field_label, '물품명')

    # 물품 제목의 최대길이 테스트
    def test_title_max_length(self):
        item = Item.objects.get(id=self.ITEM_ID)
        max_length = item._meta.get_field('title').max_length
        self.assertEquals(max_length, 50)

    # 물품 상태 최대길이 테스트
    def test_item_status_max_length(self):
        item = Item.objects.get(id=self.ITEM_ID)
        max_length = item._meta.get_field('item_status').max_length
        self.assertEquals(max_length, 3)

    # 물품 상태 디폴트값 테스트
    def test_item_status_default(self):
        item = Item.objects.get(id=self.ITEM_ID)
        item_status = item.get_item_status_display()
        self.assertEquals(item_status, 'A급')

    # 물품 재고상태 최대길이 테스트
    def test_pay_status_max_length(self):
        item = Item.objects.get(id=self.ITEM_ID)
        max_length = item._meta.get_field('pay_status').max_length
        self.assertEquals(max_length, 15)

    # 물품 재고상태 디폴트값 테스트
    def test_pay_status_default(self):
        item = Item.objects.get(id=self.ITEM_ID)
        pay_status = item.get_pay_status_display()
        self.assertEquals(pay_status, '재고있음')

    # 물품 오브젝트 이름 테스트
    def test_object_name_is_title(self):
        item = Item.objects.get(id=self.ITEM_ID)
        expected_object_name = f'{item.title}'
        self.assertEquals(expected_object_name, str(item))

    # 물품 verbose name 테스트
    def test_item_model_verbose_name(self):
        item = Item.objects.get(id=self.ITEM_ID)
        verbose_name = item._meta.verbose_name
        self.assertEquals(verbose_name, '물품')


# 물품 이미지 모델 테스트
class ItemImageModelTest(TestCase):

    # 테스트 물품 생성
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = get_user_model().objects.create(username='test', email='test@test.com')
        cate = Category.objects.create(name='testcategory')

        item = Item.objects.create(user=user, category=cate, title='testitem', amount=1000)
        cls.ITEM_ID = item.id

    # 테스트 이미지 생성
    def setUp(self):
        url = finders.find('profile/3.png')
        img = ItemImage()
        img.item = Item.objects.get(id=self.ITEM_ID)
        img.photo.save('testimg', File(open(url, 'rb')))
        img.save()
        self.IMG_ID = img.id

    # 제대로 업로드 되었는지 테스트
    def test_image_upload(self):
        p = ItemImage.objects.get(id=self.IMG_ID).photo

        # 제대로된 날짜로 업로드 되었는지 테스트
        dirname = os.path.dirname(p.url).split('/')[-1]
        try:
            dir_date = datetime.strptime(dirname, ("%Y-%m-%d")).date()
        except:
            dir_date = None
        self.assertIsNotNone(dir_date)

    # 테스트 종료후 이미지 삭제
    def tearDown(self):
        if not settings.USE_AWS:
            img = ItemImage.objects.get(id=self.IMG_ID)

            directory = os.path.dirname(img.photo.path)
            if os.path.isfile(img.photo.path):
                os.remove(img.photo.path)

            if len(os.listdir(directory)) == 0:
                os.rmdir(directory)

        return super().tearDown()


# 물품 댓글 모델 테스트
class ItemCommentModelTest(TestCase):
    DEL_ID = get_user_model().objects.get(username='deleteuser').id

    # 테스트 물품 생성, deleteuser 사용자 생성
    @classmethod
    def setUpTestData(cls):
        cate = Category.objects.create(name='전자제품')
        seller = get_user_model().objects.create(username='seller', email='seller@test.com')
        cls.item = Item.objects.create(user=seller, category=cate, title='[중고]닌텐도셋트', amount=100000)
        get_user_model().objects.create(id=cls.DEL_ID, username='deleteuser', email='deleteuser@test.com')

    # 댓글 사용자 생성, 댓글 생성
    def setUp(self):
        self.order = get_user_model().objects.create(username='order', email='order@test.com')
        cmt = ItemComment.objects.create(user=self.order, item=self.item, message='얼마에요?')
        self.CMT_ID = cmt.id

    # 댓글 사용자 삭제시 deleteuser가 있다면 댓글내용이 삭제가 되었는지 테스트
    def test_exist_deleteuser(self):
        self.order.delete()
        cmt_flag = ItemComment.objects.filter(id=self.CMT_ID).exists()
        self.assertTrue(cmt_flag)
        if cmt_flag:
            cmt = ItemComment.objects.get(id=self.CMT_ID)
            self.assertIsNotNone(cmt)
            self.assertEquals(cmt.user.username,'deleteuser')


# 주문 모델 테스트
class OrderModelTest(TestCase):

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

    # 계좌이체시 item 재고 상태 테스트
    def test_bank_trans(self):
        self.trade.update()
        self.assertEquals(self.trade.item.pay_status, 'reservation')

    # 결제완료시 item 재고 상태 테스트
    def test_bank_trans_paid(self):
        self.trade.status = 'paid'
        self.trade.update()
        self.assertEquals(self.trade.item.pay_status, 'reservation')

    # 거래완료시 item 재고 상태 테스트
    def test_bank_trans_success(self):
        self.trade.status = 'success'
        self.trade.update()
        self.assertEquals(self.trade.item.pay_status, 'sale_complete')

    # 거래취소시 item 재고 상태 테스트
    def test_bank_trans_cancelled(self):
        self.trade.cancel()
        self.assertEquals(self.trade.item.pay_status, 'ready')
