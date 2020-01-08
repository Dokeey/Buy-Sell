from django.test import TestCase

class StoreProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        users = get_user_model().objects.create(username='testuser', email='test@test.com')
        store = StoreProfile.objects.create(user=users, name='teststore')

    #max_length
    def test_storeprofile_name_max_length(self):
        storeprofile = StoreProfile.objects.get(name='teststore')
        max_length = storeprofile._meta.get_field('name').max_length
        self.assertEquals(max_length, 20)

    def test_storeprofile_comment_max_length(self):
        storeprofile = StoreProfile.objects.get(name='teststore')
        max_length = storeprofile._meta.get_field('comment').max_length
        self.assertEquals(max_length, 200)

    #default 값
    def test_storeprofile_comment_defalut(self):
        storeprofile = StoreProfile.objects.get(name='teststore')
        default = storeprofile._meta.get_field('comment').default
        self.assertEquals(default, '반갑습니다.')


