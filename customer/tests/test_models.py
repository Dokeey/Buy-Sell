from django.test import TestCase
from customer.models import CustomerCategory, CustomerAsk, CustomerFAQ, CustomerNotice
from django.contrib.auth import get_user_model

class CustomerCategoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cate = CustomerCategory.objects.create(name='testcustomercate')
        chillcate = CustomerCategory.objects.create(name='chillcate', parent=cate)

    #max_length
    def test_customer_category_max_length(self):
        cate = CustomerCategory.objects.get(id=1)
        max_length = cate._meta.get_field('name').max_length
        self.assertEquals(max_length, 50)

class CutomerFAQTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cate = CustomerCategory.objects.create(name='testFAQcate')
        FAQ = CustomerFAQ.objects.create(faq_title='testfaq', faq_category=cate,faq_content='test')

    #max_length
    def test_customer_FAQ_title_max_length(self):
        faq = CustomerFAQ.objects.get(id=1)
        max_length = faq._meta.get_field('faq_title').max_length
        self.assertEquals(max_length, 40)

class CutomerAskTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create(username='test', email='test@test.com')
        cate = CustomerCategory.objects.create(name='testAskcate')
        ask = CustomerAsk.objects.create(author=author, ask_category=cate, ask_title='test', ask_post='test')
        
    #max_length
    def test_customer_ask_title_max_length(self):
        ask = CustomerAsk.objects.get(id=1)
        max_length = ask._meta.get_field('ask_title').max_length
        self.assertEquals(max_length, 100)

    def test_customer_ask_going_max_length(self):
        ask = CustomerAsk.objects.get(id=1)
        max_length = ask._meta.get_field('ask_going').max_length
        self.assertEquals(max_length, 20)

    #default
    def test_customer_ask_going_default(self):
        ask = CustomerAsk.objects.get(id=1)
        default = ask._meta.get_field('ask_going').default
        self.assertEquals(default, 'ready')

class CustomerNoticeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        notice = CustomerNotice.objects.create(notice_title='title', notice_content='content')

    #max_length
    def test_customer_notice_max_length(self):
        notice = CustomerNotice.objects.get(id=1)
        max_length = notice._meta.get_field('notice_title').max_length
        self.assertEquals(max_length, 40)