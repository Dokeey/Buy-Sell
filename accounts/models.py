from django.conf import settings
from django.contrib.auth import user_logged_in, get_user_model
from django.contrib.auth.models import AbstractUser, UserManager as AuthUserManager
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator, _lazy_re_compile, MaxLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class UserManager(AuthUserManager):
    #User = get_user_model()

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('phone', 0)
        extra_fields.setdefault('address', 'blank')
        extra_fields.setdefault('account_num', 0)

        return super().create_superuser(username, email, password, **extra_fields)


def id_validate(value):
    user = get_user_model()
    user = user.objects.filter(nic_name=value)
    if user:
        raise ValidationError(
            _("'{}' is already exists.".format(value)),
        )
    return None


phone_validate = RegexValidator(
            regex=r'^0\d{10,11}$',
            message='정확한 연락처를 적어주세요.',
            code='invalid_phone'
)


class User(AbstractUser):
    nic_name = models.CharField(max_length=10, unique=True, validators=[id_validate])
    phone = models.CharField(max_length=11, validators=[phone_validate])
    address = models.CharField(max_length=100)
    account_num = models.CharField(max_length=20, validators=[MaxLengthValidator(20)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    object = UserManager()



class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    session_key = models.CharField(max_length=40, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

def kicked_my_other_sessions(sender, request, user, **kwargs):
    user.is_user_logged_in = True

user_logged_in.connect(kicked_my_other_sessions)