import os

from django.test import TestCase
from store.models import StoreProfile
from django.contrib.auth import get_user_model
from store.forms import StoreProfileForm, StoreQuestionForm, StoreGradeForm
from django.contrib.staticfiles import finders
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

class StoreProfileFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects.create(username='testuser', email='test@test.com')
        url = finders.find('profile/3.png')
        img = StoreProfile()
        img.user = users
        img.name = 'teststore'
        img.photo.save('testimg', File(open(url,'rb')))
        img.save()
        cls.store_id = img.id

    def test_storeprofile_form_name_field_label(self):
        form = StoreProfileForm()
        self.assertTrue(form.fields['name'].label == '가게 이름')

    def test_storeprofile_form_photo_field_label(self):
        form = StoreProfileForm()
        self.assertTrue(form.fields['photo'].label == '가게 사진')

    def test_storeprofile_form_comment_field_label(self):
        form = StoreProfileForm()
        self.assertTrue(form.fields['comment'].label == '가게 소개')

    def test_storeprofile_data(self):
        url = finders.find('profile/3.png')
        photo_file = open(url, 'rb')
        post_dict = {'name':'test', 'comment': 'hi'}
        file_dict = {'photo': SimpleUploadedFile(photo_file.name, photo_file.read())}
        form = StoreProfileForm(post_dict, file_dict)
       

        self.assertTrue(form.is_valid())
        storeprofile = form.save(commit = False)
        storeprofile.store_profile_id = self.store_id

        self.assertEqual(storeprofile.name, 'test')
        self.assertEqual(storeprofile.photo.url, '/media/3.png')
        self.assertEqual(storeprofile.comment, 'hi')

    def test_storeprofile_empty_data(self):
        form = StoreProfileForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,{'name': ['필수 항목입니다.'], 'photo':  ['필수 항목입니다.']})

    #media storeprofile에 저장되는 test image 삭제
    def tearDown(self):
        img = StoreProfile.objects.get(id=self.store_id)
        directory = os.path.dirname(img.photo.path)
        if os.path.isfile(img.photo.path):
            os.remove(img.photo.path)

        if len(os.listdir(directory)) == 0:
            os.rmdir(directory)

        super().tearDown()

class StoreQuestionFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects.create(username='testuser', email='test@test.com')
        store = StoreProfile.objects.create(user=users, name='teststore')
        cls.store_id = store.id

    #폼에 데이터 넣어보고 확인
    def test_storequestion_form_data(self):
        form = StoreQuestionForm({
            'comment': 'ok good'
        })
        self.assertTrue(form.is_valid())
        storequestion = form.save(commit=False)
        storequestion.store_profile_id = self.store_id
        self.assertEqual(storequestion.comment, 'ok good')

    #폼에 빈 데이터 넣어보고 확인
    def test_storequestion_form_empty_data(self):
        form = StoreQuestionForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,{'comment': ['필수 항목입니다.']})

class StoreGradeFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects.create(username='testuser', email='test@test.com')
        store = StoreProfile.objects.create(user=users, name='teststore')
        cls.store_id = store.id

    def test_storegrade_form_data(self):
        form = StoreGradeForm({
            'grade_comment': 'ok good'
        })
        self.assertTrue(form.is_valid())
        storegrade = form.save(commit=False)
        storegrade.store_profile_id = self.store_id
        self.assertEqual(storegrade.grade_comment, 'ok good')

    def test_storegrade_form_empty_data(self):
        form = StoreGradeForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,{'grade_comment': ['필수 항목입니다.']})