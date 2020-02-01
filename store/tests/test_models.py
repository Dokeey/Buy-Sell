from django.test import TestCase

from trade.models import Item
from category.models import Category
from store.models import StoreProfile, QuestionComment, StoreGrade
from django.contrib.auth import get_user_model

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

    #/static/profile/{}.png
    # def test_storeprofile_photo_default(self):
    #     sp = StoreProfile.objects.get(id=1)
    #     image = sp.photo.path
    #     self.failUnless(open(image), 'file not found')

class QuestionCommentTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        users = get_user_model().objects.create(username='testuser', email='test@test.com')
        store = StoreProfile.objects.create(user=users ,name='testuserstore')

        users2 = get_user_model().objects.create(username='testuser2', email='test2@test.com')
        store2 = StoreProfile.objects.create(user=users2 ,name='testuserstore2')

        deluser = get_user_model().objects.create(id=3, username='deleteuser', email='del@del.com')
        delstore = StoreProfile.objects.create(user=deluser, name='deleteuser의 가게')

        #Comment 생성
        comment = QuestionComment.objects.create(store_profile=store2, author=users, comment='hi')
        comment1 = QuestionComment.objects.create(store_profile=store, author=users2, comment='hi')
        reply = QuestionComment.objects.create(store_profile=store2, author=users, comment='re hi', parent=comment)

        cls.users_id=users.id
        cls.comment_id = comment.id
        cls.reply_id = reply.id
    #max_length
    def test_questioncomment_comment_max_length(self):
        questioncomment = QuestionComment.objects.get(id=self.comment_id)
        max_length = questioncomment._meta.get_field('comment').max_length
        self.assertEquals(max_length, 1000)

    #대댓글
    def test_questioncomment_recomment(self):
        questioncomment = QuestionComment.objects.get(id=self.reply_id)
        self.assertEquals(questioncomment.parent.pk, self.comment_id)

    # deleteuser
    def test_storecomment_delete_user(self):
        user = get_user_model().objects.get(id=self.users_id)
        user.delete()
        delcomment = QuestionComment.objects.get(id=self.comment_id)
        self.assertEquals(delcomment.author.username, 'deleteuser')

class StoreGradeTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        users = get_user_model().objects.create(username='testuser', email='test@test.com')
        store = StoreProfile.objects.create(user=users ,name='testuserstore')
        cls.users_id=users.id

        users2 = get_user_model().objects.create(username='testuser2', email='test2@test.com')
        store2 = StoreProfile.objects.create(user=users2 ,name='testuserstore2')

        deluser = get_user_model().objects.create(id=3, username='deleteuser', email='del@del.com')
        delstore = StoreProfile.objects.create(user=deluser, name='deleteuser의 가게')
 
        #grade 모델을 위한 생성
        cate = Category.objects.create(name='testcate')
        item = Item.objects.create(user=users2, title='testitem', category=cate, amount='10')
        #grade 생성
        grade = StoreGrade.objects.create(store_profile=store2, author=users, store_item=item, grade_comment='hi')
        cls.grade_id=grade.id

    # max_length
    def test_storegrade_grade_comment_max_length(self):
        storegrade = StoreGrade.objects.get(id=1)
        max_length = storegrade._meta.get_field('grade_comment').max_length
        self.assertEquals(max_length, 250)

    #default
    def test_storegrade_rating_default(self):
        storegrade = StoreGrade.objects.get(id=1)
        default = storegrade._meta.get_field('rating').default
        self.assertEquals(default, 0)

    #deleteuser
    def test_storegrade_delete_user(self):
        user = get_user_model().objects.get(id=self.users_id)
        user.delete()
        delgrade = StoreGrade.objects.get(id=self.grade_id)
        self.assertEquals(delgrade.author.username, 'deleteuser')
