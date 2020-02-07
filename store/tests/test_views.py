import os
import json
from django.test import TestCase
from django.urls import reverse

from django.contrib.staticfiles import finders
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from hitcount.models import HitCount
from django.contrib.auth import get_user_model

from category.models import Category
from mypage.models import Follow
from store.models import StoreProfile, StoreGrade
from django.contrib.contenttypes.models import ContentType

from trade.models import Item, Order, ItemImage


#========= 인기가게 테스트 ==========

class StarStoreSearchListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        users = get_user_model().objects.create(username=f'test1', email=f't1@test.com')
        store = StoreProfile.objects.create(user=users, name=f'test1')
        cls.store_id = store.pk

    def test_empty_query_redirect(self):
        response = self.client.get(reverse('store:star_store_search'), {'query':''})
        # self.assertRedirects(response, reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 302)

    def test_only_space_query_redirect(self):
        response = self.client.get(reverse('store:star_store_search'), {'query':'     '})
        # self.assertRedirects(response, reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 302)

    def test_name_filter(self):
        response = self.client.get(reverse('store:star_store_search'), {'query':'1'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['star_search'], ['<StoreProfile: test1>'] )

    def tearDown(self):
        img = StoreProfile.objects.get(pk=self.store_id)
        if img.photo:
            directory = os.path.dirname(img.photo.path)
            if os.path.isfile(img.photo.path):
                os.remove(img.photo.path)

            if len(os.listdir(directory)) == 0:
                os.rmdir(directory)

        super().tearDown()

class StarStoreHitListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # number_of_users = 3

        # for user_id in range(number_of_users):
        #     users = get_user_model().objects.create_user(username=f'test{user_id}', email=f't{user_id}@test.com', password='Test1234')
        #     stores = StoreProfile.objects.create(user=users, name=f'test{user_id}')

        user0 = get_user_model().objects.create_user(username='test0', email='t00@test.com', password='Test1234')
        store0 = StoreProfile.objects.create(user=user0, name='test0')
        cls.store0 = store0

        user1 = get_user_model().objects.create_user(username='test1', email='t01@test.com', password='Test1234')
        store1 = StoreProfile.objects.create(user=user1, name='test1')
        cls.store1 = store1

        user2 = get_user_model().objects.create_user(username='test2', email='t02@test.com', password='Test1234')
        store2 = StoreProfile.objects.create(user=user2, name='test2')
        cls.store2 = store2

    def test_hit_count(self):
        response = self.client.get(reverse('store:store_sell_list', args=[self.store0.pk]))
        self.assertEqual(response.status_code, 200)

        ctype = ContentType.objects.get_for_model(StoreProfile)

        self.assertQuerysetEqual(HitCount.objects.filter(content_type=ctype).values('object_pk','hits'),
                                 ["{'object_pk': "+str(self.store0.pk)+", 'hits': 1}"])

    def test_star_store_hit_rank(self):

        # test1가 test0번의 가게만 방문
        self.login = self.client.login(username='test1', password='Test1234')
        self.assertEqual(self.login, True)
        self.client.get(reverse('store:store_sell_list', args=[self.store0.pk]))

        self.client.logout()

        # test2가 test0번과 test1번의 가게 방문
        self.login = self.client.login(username='test2', password='Test1234')
        self.assertEqual(self.login, True)

        self.client.get(reverse('store:store_sell_list', args=[self.store0.pk]))
        self.client.get(reverse('store:store_sell_list', args=[self.store1.pk]))

        self.client.logout()

        #rank 확인하러 인기가게 hit 페이지 방문
        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 200)

        for store in response.context['stores']:
            if store.pk == self.store0.pk:
                test0_rank = store.rank
            if store.pk == self.store1.pk :
                test1_rank = store.rank


        self.assertEqual(test0_rank, 1)

        self.assertEqual(test1_rank, 2)

    def test_star_store_hit_my_rank(self):

        #test0의 hit 수 1 증가
        self.client.login(username='test1')
        self.client.get(reverse('store:store_sell_list', args=[self.store0.pk]))
        self.client.logout()

        #순위권인 유저의 my rank 확인
        self.login = self.client.login(username='test0', password='Test1234')
        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.login, True)

        self.assertEqual(response.context['my_rank'], 1)
        self.client.logout()

        # #비순위권인 유저의 my rank 확인
        # self.login = self.client.login(username='test1', password='Test1234')
        # response = self.client.get(reverse('store:star_store_hit'))
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.login, True)
        #
        # self.assertEqual(response.context['my_rank'], '-')


    def test_star_store_hit_no_rank(self):

        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:store_error'))

    def tearDown(self):
        stores = StoreProfile.objects.all()
        for store in stores:
            if store.photo:
                img = store.photo
                directory = os.path.dirname(img.path)
                if os.path.isfile(img.path):
                    os.remove(img.path)

                if len(os.listdir(directory)) == 0:
                    os.rmdir(directory)

        super().tearDown()

class StarStoreGradeListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        user0 = get_user_model().objects.create_user(username='test0', email='t00@test.com', password='Test1234')
        store0 = StoreProfile.objects.create(user=user0, name='test0')
        cls.store0 = store0

        user1 = get_user_model().objects.create_user(username='test1', email='t01@test.com', password='Test1234')
        store1 = StoreProfile.objects.create(user=user1, name='test1')    
        cls.store1 = store1

    def test_star_store_grade_rank(self):
        
        make_rank1 = StoreGrade.objects.create(store_profile=self.store0, author=self.store1.user, grade_comment='test rank', rating=4)
        make_rank2 = StoreGrade.objects.create(store_profile=self.store0, author=self.store1.user, grade_comment='test rank', rating=1)

        make_rank3 = StoreGrade.objects.create(store_profile=self.store1, author=self.store0.user, grade_comment='test rank', rating=5)
        
        response = self.client.get(reverse('store:star_store_grade'))
        
        for store in response.context['stores'] :
            if store.pk == self.store0.pk:
                store0_rank = store.rank
            if store.pk == self.store1.pk:
                store1_rank = store.rank
        
        self.assertEqual(store0_rank, 2)
        self.assertEqual(store1_rank, 1)

    def test_star_store_grade_no_data(self):

        response = self.client.get(reverse('store:star_store_grade'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:store_error'))

    def test_star_store_grade_my_rank(self):

        #test0의 평점 생성
        test_rank = StoreGrade.objects.create(store_profile=self.store0, author=self.store1.user, grade_comment='test rank', rating=5)

        #순위권 유저의 my rank 확인
        self.client.login(username='test0', password='Test1234')
        response = self.client.get(reverse('store:star_store_grade'))
        self.assertEqual(response.context['my_rank'], 1)
        self.client.logout()

        # #비순위권 유저의 my rank 확인
        # self.client.login(username='test1', password='Test1234')
        # response = self.client.get(reverse('store:star_store_grade'))
        # self.assertEqual(response.context['my_rank'], '-')
        # self.client.logout()

    def tearDown(self):
        stores = StoreProfile.objects.all()
        for store in stores:
            if store.photo:
                img = store.photo
                if os.path.isfile(img.path):
                    os.remove(img.path)
        super().tearDown()

class StarStoreSellListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        user0 = get_user_model().objects.create_user(username='test0', email='t00@test.com', password='Test1234')
        store0 = StoreProfile.objects.create(user=user0, name='test0')
        cls.store0 = store0

        user1 = get_user_model().objects.create_user(username='test1', email='t01@test.com', password='Test1234')
        store1 = StoreProfile.objects.create(user=user1, name='test1')
        cls.store1 = store1

    def test_star_store_sell_rank(self):

        self.client.login(username='test1', password='Test1234')

        cate = Category.objects.create(name='testcategory')
        item = Item.objects.create(user=self.store0.user, category=cate, title='testitem', amount=1000, pay_status='sale_complete')
        order = Order.objects.create(user=self.store1.user,
                                     username='awef',
                                     phone='0123',
                                     post_code='213',
                                     address='123',
                                     detail_address='123',
                                     amount=1000,
                                     item=item,
                                     pay_choice='bank_trans',
                                     status='success',
                                     is_active=True
                                     )

        url = finders.find('profile/3.png')
        itemimage = ItemImage.objects.create(item=item)
        itemimage.photo.save('testimg', File(open(url, 'rb')))
        itemimage.save()

        # response = self.client.get(reverse('trade:order_confirm', kwargs={'order_id': order.id}), follow=True)
        # self.assertEquals(list(response.context.get('messages'))[0].message, '구매를 축하드립니다!!')
        # self.assertEquals(Order.objects.get(id=order.id).status, 'success')

        ################
        self.assertEquals(Order.objects.get(id=order.id).status, 'success')
        ################

        response = self.client.get(reverse('store:star_store_sell'))
        for store in response.context['stores']:
            if store == self.store0:
                store0_rank = store.rank
        self.assertEqual(store0_rank, 1)

    def test_star_store_sell_no_data(self):

        response = self.client.get(reverse('store:star_store_sell'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:store_error'))

    def test_star_store_sell_my_rank(self):
        self.client.login(username='test1', password='Test1234')

        cate = Category.objects.create(name='testcategory')
        item = Item.objects.create(user=self.store0.user, category=cate, title='testitem', amount=1000, pay_status='sale_complete')
        order = Order.objects.create(user=self.store1.user,
                                     username='awef',
                                     phone='0123',
                                     post_code='213',
                                     address='123',
                                     detail_address='123',
                                     amount=1000,
                                     item=item,
                                     pay_choice='bank_trans',
                                     status='success',
                                     is_active=True
                                     )

        url = finders.find('profile/3.png')
        itemimage = ItemImage.objects.create(item=item)
        itemimage.photo.save('testimg', File(open(url, 'rb')))
        itemimage.save()
        response = self.client.get(reverse('store:star_store_sell'))
        self.assertEqual(response.context['my_rank'], '-')

        self.client.logout()

        self.client.login(username='test0', password='Test1234')
        response = self.client.get(reverse('store:star_store_sell'))
        self.assertEqual(response.context['my_rank'], 1)

        img = ItemImage.objects.get(pk=itemimage.pk)
        directory = os.path.dirname(img.photo.path)
        if os.path.isfile(img.photo.path):
            os.remove(img.photo.path)

        if len(os.listdir(directory)) == 0:
            os.rmdir(directory)
    def tearDown(self):
        items = ItemImage.objects.all()
        for item in items:
            if item.photo:
                img = item.photo
                directory = os.path.dirname(img.path)
                if os.path.isfile(img.path):
                    os.remove(img.path)

        stores = StoreProfile.objects.all()
        for store in stores:
            if store.photo:
                img = store.photo
                directory = os.path.dirname(img.path)
                if os.path.isfile(img.path):
                    os.remove(img.path)



        super().tearDown()

class StarStoreFollowListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user0 = get_user_model().objects.create_user(username='test0', email='t00@test.com', password='Test1234')
        store0 = StoreProfile.objects.create(user=user0, name='test0')
        cls.store0 = store0

        user1 = get_user_model().objects.create_user(username='test1', email='t01@test.com', password='Test1234')
        store1 = StoreProfile.objects.create(user=user1, name='test1')
        cls.store1 = store1

    def test_star_store_follow_rank(self):

        make_follow = Follow.objects.create(user=self.store1.user, store=self.store0)

        response = self.client.get(reverse('store:star_store_follow'))
        for store in response.context['stores']:
            if store == self.store0:
                store0_rank = store.rank
        self.assertEqual(store0_rank, 1)

    def test_star_store_follow_no_data(self):
        response = self.client.get(reverse('store:star_store_follow'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:store_error'))

    def test_star_store_follow_my_rank(self):

        make_follow = Follow.objects.create(user=self.store1.user, store=self.store0)

        self.client.login(username='test0', password='Test1234')
        response = self.client.get(reverse('store:star_store_follow'))
        self.assertEqual(response.context['my_rank'], 1)
        self.client.logout()

    def tearDown(self):
        stores = StoreProfile.objects.all()
        for store in stores:
            if store.photo:
                img = store.photo
                directory = os.path.dirname(img.path)
                if os.path.isfile(img.path):
                    os.remove(img.path)

                if len(os.listdir(directory)) == 0:
                    os.rmdir(directory)

        super().tearDown()

#========= 스토어 프로필 테스트 ==========

class StoreSellListViewTest(TestCase):
    #ordering
    #item list
    @classmethod
    def setUpTestData(cls):

        user0 = get_user_model().objects.create_user(username='test0', email='t00@test.com', password='Test1234')
        store0 = StoreProfile.objects.create(user=user0, name='test0')
        cls.store0 = store0

        cate = Category.objects.create(name='testcategory')
        item = Item.objects.create(user=user0, category=cate, title='testitem', amount=1000,
                                   pay_status='sale_complete')
        url = finders.find('profile/3.png')
        itemimage = ItemImage.objects.create(item=item)
        itemimage.photo.save('testimg', File(open(url, 'rb')))
        itemimage.save()
        cls.itemimg = itemimage

    def test_sell_list(self):
        response = self.client.get(reverse('store:store_sell_list', kwargs={'pk':self.store0.pk}))
        self.assertEqual(response.context['stores'], self.store0)
        self.assertQuerysetEqual(response.context['items'], ['<Item: testitem>'])

    def tearDown(self):
        img = ItemImage.objects.get(pk=self.itemimg.pk)
        directory = os.path.dirname(img.photo.path)
        if os.path.isfile(img.photo.path):
            os.remove(img.photo.path)

        if len(os.listdir(directory)) == 0:
            os.rmdir(directory)

        img = StoreProfile.objects.get(pk=self.store0.pk)
        directory = os.path.dirname(img.photo.path)
        if os.path.isfile(img.photo.path):
            os.remove(img.photo.path)

        if len(os.listdir(directory)) == 0:
            os.rmdir(directory)
        super().tearDown()

class StoreProfileEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        user0 = get_user_model().objects.create_user(username='test0', email='t00@test.com', password='Test1234')
        store0 = StoreProfile.objects.create(user=user0, name='test0store')
        cls.store0 = store0

    def test_store_profile_edit(self):

        self.client.login(username='test0', password='Test1234')
        url = finders.find('profile/3.png')
        img = File(open(url, 'rb'))
        postresponse = self.client.post(reverse('store:store_profile_edit'),
                                        {'name':'yejin','photo':img,'comment':'hi'})

        self.assertEqual(postresponse.status_code, 200)
        self.assertEquals(
            json.loads(str(postresponse.content, encoding='utf-8'))['is_valid'],
            True
        )
        response = self.client.get(reverse('store:store_sell_list', kwargs={'pk': self.store0.pk}))

        self.assertEqual(response.context['stores'].name, 'yejin')

    def test_store_profile_edit_nologin(self):

        response = self.client.get(reverse('store:store_profile_edit'))
        self.assertRedirects(response, '/accounts/login/?next=/store/profile/edit/')

    def tearDown(self):
        for index in range(0,6):
            img = StoreProfile.objects.get(pk=self.store0.pk)
            if img.photo:
                directory = os.path.dirname(img.photo.path)
                if os.path.isfile(img.photo.path):
                    os.remove(img.photo.path)

                if len(os.listdir(directory)) == 0:
                    os.rmdir(directory)

        super().tearDown()












