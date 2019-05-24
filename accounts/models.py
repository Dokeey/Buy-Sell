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
