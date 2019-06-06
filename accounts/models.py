from django.conf import settings
from django.contrib.auth import user_logged_in, get_user_model
from django.contrib.auth.models import AbstractUser, UserManager as AuthUserManager
from django.core.validators import RegexValidator, MaxLengthValidator
from django.db import models
from django.utils.crypto import get_random_string
from store.models import StoreProfile

# Create your models here.


class UserManager(AuthUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        nick_name = get_random_string(length=10)
        while Profile.objects.filter(nick_name=nick_name):
            nick_name = get_random_string(length=10)

        Profile.objects.create(user=user, email=email, phone='0', address='', nick_name=nick_name, account_num='0')
        StoreProfile.objects.create(user=user, name=user.profile.nick_name + '의 가게')

        return user


phone_validate = RegexValidator(
    regex=r'^0\d{8,10}$',
    message='정확한 연락처를 적어주세요.',
    code='invalid_phone'
)

class User(AbstractUser):
    object = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=10, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=11, validators=[phone_validate])
    post_code = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    detail_address = models.CharField(max_length=20)
    account_num = models.CharField(max_length=20, validators=[MaxLengthValidator(20)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nick_name

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    session_key = models.CharField(max_length=40, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

def kicked_my_other_sessions(sender, request, user, **kwargs):
    user.is_user_logged_in = True

user_logged_in.connect(kicked_my_other_sessions)

