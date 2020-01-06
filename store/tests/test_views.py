from django.test import TestCase
from django.urls import reverse

from hitcount.models import HitCount
from django.contrib.auth import get_user_model
from store.models import StoreProfile
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
        #hit 인기순위 잘 나오는지
        #마이 히트가 잘 나오는지
        number_of_users = 3

        for user_id in range(number_of_users):
            users = get_user_model().objects.create(username=f'test{user_id}', email=f't{user_id}@test.com', is_active=True)
            users.set_password('Test1234')
            users.save()
            StoreProfile.objects.create(user=users, name=f'test{user_id}')
        
    def test_hit_count(self):

        response = self.client.get(reverse('store:store_sell_list', args=['11']))
        self.assertEqual(response.status_code, 200)

        ctype = ContentType.objects.get_for_model(StoreProfile)

        self.assertQuerysetEqual(HitCount.objects.filter(content_type=ctype).values('object_pk','hits'), ["{'object_pk': 11, 'hits': 1}"])
    
    def test_star_store_hit_rank(self):

        # test1가 test0번의 가게만 방문
        self.login = self.client.login(username='test1', password='Test1234')
        self.assertEqual(self.login, True)
        self.client.get(reverse('store:store_sell_list', args=['11']))
        
        self.client.logout()

        # test2가 test0번과 test1번의 가게 방문
        self.login = self.client.login(username='test2', password='Test1234')
        self.assertEqual(self.login, True)
        
        self.client.get(reverse('store:store_sell_list', args=['11']))
        self.client.get(reverse('store:store_sell_list', args=['12']))

        self.client.logout()

        #rank 확인하러 인기가게 hit 페이지 방문
        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 200)

        for i in response.context['stores']:
            if i['object_pk'] == 11:
                test0_rank = i['rank']
            if i['object_pk'] == 12 :
                test1_rank = i['rank']

        self.assertEqual(test0_rank, 1)

        self.assertEqual(test1_rank, 2)
        
    
    def test_star_store_hit_my_no_rank(self):

        self.client.get(reverse('store:store_sell_list', args=['11']))
        
        self.login = self.client.login(username='test1', password='Test1234')
        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.login, True)
        
        self.assertEqual(response.context['my_hit'], '-')
        

    def test_star_store_hit_my_rank(self):

        self.client.login(username='test1')
        self.client.get(reverse('store:store_sell_list', args=['11']))
        self.client.logout()

        self.login = self.client.login(username='test0', password='Test1234')
        response = self.client.get(reverse('store:star_store_hit'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.login, True)
        
        self.assertEqual(response.context['my_hit'], 1)
        self.client.logout()