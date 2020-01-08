from django.test import TestCase
from django.urls import reverse

from hitcount.models import HitCount
from django.contrib.auth import get_user_model
from store.models import StoreProfile, StoreGrade
from django.contrib.contenttypes.models import ContentType


class StarStoreSearchListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_ob_users = 8

        for user_id in range(number_ob_users):
            users = get_user_model().objects.create(username=f'test{user_id}', email=f't{user_id}@test.com')
            StoreProfile.objects.create(user=users, name=f'test{user_id}')

    def test_view_pagination_is_(self):
        response = self.client.get(reverse('store:star_store_search'), {'query':'test'})
        self.assertEqual(response.status_code, 200)

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

        self.assertQuerysetEqual(HitCount.objects.filter(content_type=ctype).values('object_pk','hits'), ["{'object_pk': 11, 'hits': 1}"])
    
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

        for i in response.context['stores']:
            if i['object_pk'] == self.store0.pk:
                test0_rank = i['rank']
            if i['object_pk'] == self.store1.pk :
                test1_rank = i['rank'] 
        

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
        
        self.assertEqual(response.context['my_hit'], 1)
        self.client.logout()

        #비순위권인 유저의 my rank 확인
        self.login = self.client.login(username='test1', password='Test1234')
        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.login, True)
        
        self.assertEqual(response.context['my_hit'], '-')


    def test_star_store_hit_no_rank(self):

        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:store_error'))

class TestStarStoreGradeListView(TestCase):
    @classmethod
    def setUpTestData(cls):

        user0 = get_user_model().objects.create_user(username='test0', email='t00@test.com', password='Test1234')
        store0 = StoreProfile.objects.create(user=user0, name='test0')
        cls.store0 = store0

        user1 = get_user_model().objects.create_user(username='test1', email='t01@test.com', password='Test1234')
        store1 = StoreProfile.objects.create(user=user1, name='test1')    
        cls.store1 = store1

        user2 = get_user_model().objects.create_user(username='test2', email='t02@test.com', password='Test1234')
        store2 = StoreProfile.objects.create(user=user2, name='test2')
        cls.store2 = store2
        

    def test_star_store_grade_rank(self):
        
        make_rank1 = StoreGrade.objects.create(store_profile=self.store0, author=self.store1.user, grade_comment='test rank', rating=4)
        make_rank2 = StoreGrade.objects.create(store_profile=self.store0, author=self.store1.user, grade_comment='test rank', rating=1)

        make_rank3 = StoreGrade.objects.create(store_profile=self.store1, author=self.store0.user, grade_comment='test rank', rating=5)
        
        response = self.client.get(reverse('store:star_store_grade'))
        
        for store in response.context['stores'] :
            if store['store_info'] == self.store0:
                store0_rank = store['rank']
            if store['store_info'] == self.store1:
                store1_rank = store['rank']
        
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
        self.assertEqual(response.context['my_grade'], 1)
        self.client.logout()

        self.client.login(username='test1', password='Test1234')
        response = self.client.get(reverse('store:star_store_grade'))
        self.assertEqual(response.context['my_grade'], '-')