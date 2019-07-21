from django.conf import settings
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import AbstractUser, UserManager as AuthUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator, MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string

# Create your models here.
from .validators import phone_validate


class UserManager(AuthUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)


        Profile.objects.create(user=user, phone='0123456789', post_code='', address='', detail_address='',  account_num='0')

        from store.models import StoreProfile
        StoreProfile.objects.create(user=user, name=user.username + '의 가게')

        return user


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=15,
        unique=True,
        help_text=_('Required. 15 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), unique=True)
    object = UserManager()


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, validators=[phone_validate])
    post_code = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    detail_address = models.CharField(max_length=20)
    account_num = models.CharField(max_length=20, validators=[MaxLengthValidator(20)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    session_key = models.CharField(max_length=40, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

def kicked_my_other_sessions(sender, request, user, **kwargs):
    user.is_user_logged_in = True

user_logged_in.connect(kicked_my_other_sessions)

