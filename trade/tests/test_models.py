import os

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.core.files import File
from django.test import TestCase

from category.models import Category
from trade.models import Item, ItemImage, ItemComment, Order

class ItemModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = get_user_model().objects.create(username='test', email='test@test.com')
        cate = Category.objects.create(name='testcategory')

        item = Item.objects.create(user=user, category=cate, title='testitem', amount=1000)
        cls.ITEM_ID = item.id

    def test_title_label(self):
        item = Item.objects.get(id=self.ITEM_ID)
        field_label = item._meta.get_field('title').verbose_name
        self.assertEquals(field_label, '물품명')

    def test_title_max_length(self):
        item = Item.objects.get(id=self.ITEM_ID)
        max_length = item._meta.get_field('title').max_length
        self.assertEquals(max_length, 50)

    def test_item_status_max_length(self):
        item = Item.objects.get(id=self.ITEM_ID)
        max_length = item._meta.get_field('item_status').max_length
        self.assertEquals(max_length, 3)

    def test_item_status_default(self):
        item = Item.objects.get(id=self.ITEM_ID)
        item_status = item.get_item_status_display()
        self.assertEquals(item_status, 'A급')

    def test_pay_status_max_length(self):
        item = Item.objects.get(id=self.ITEM_ID)
        max_length = item._meta.get_field('pay_status').max_length
        self.assertEquals(max_length, 15)

    def test_pay_status_default(self):
        item = Item.objects.get(id=self.ITEM_ID)
        pay_status = item.get_pay_status_display()
        self.assertEquals(pay_status, '재고있음')

    def test_object_name_is_title(self):
        item = Item.objects.get(id=self.ITEM_ID)
        expected_object_name = f'{item.title}'
        self.assertEquals(expected_object_name, str(item))

    def test_item_model_verbose_name(self):
        item = Item.objects.get(id=self.ITEM_ID)
        verbose_name = item._meta.verbose_name
        self.assertEquals(verbose_name, '물품')


class ItemImageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = get_user_model().objects.create(username='test', email='test@test.com')
        cate = Category.objects.create(name='testcategory')

        item = Item.objects.create(user=user, category=cate, title='testitem', amount=1000)
        cls.ITEM_ID = item.id

    def setUp(self):
        url = finders.find('profile/3.png')
        img = ItemImage()
        img.item = Item.objects.get(id=self.ITEM_ID)
        img.photo.save('testimg', File(open(url, 'rb')))
        img.save()

    def test_image_upload(self):
        p = ItemImage.objects.get(id=self.ITEM_ID).photo.path
        self.failUnless(open(p), 'file not found')

    def tearDown(self):
        img = ItemImage.objects.get(id=self.ITEM_ID)
        directory = os.path.dirname(img.photo.path)
        if os.path.isfile(img.photo.path):
            os.remove(img.photo.path)

        if len(os.listdir(directory)) == 0:
            os.rmdir(directory)

        super().tearDown()


class ItemCommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = get_user_model().objects.create(username='test', email='test@test.com')
        cate = Category.objects.create(name='testcategory')

        item = Item.objects.create(user=user, category=cate, title='testitem', amount=1000)
        cmt = ItemComment.objects.create(user=user, item=item, message='test')
        cls.cmt = cmt.id

    def test_title_label(self):
        cmt = ItemComment.objects.get(id=self.cmt)
        field_label = cmt._meta.get_field('title').verbose_name
        self.assertEquals(field_label, '물품명')