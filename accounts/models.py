from django.conf import settings
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import AbstractUser, UserManager as AuthUserManager
from django.db import models

# Create your models here.


class UserManager(AuthUserManager):
    #User = get_user_model()

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('nic_name', 'hello')
        extra_fields.setdefault('phone', 0)
        extra_fields.setdefault('address', 'blank')
        extra_fields.setdefault('account_num', 0)

        return super().create_superuser(username, email, password, **extra_fields)

class User(AbstractUser):
    nic_name = models.CharField(max_length=10)
    phone = models.PositiveIntegerField()
    address = models.CharField(max_length=100)
    account_num = models.PositiveIntegerField()
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