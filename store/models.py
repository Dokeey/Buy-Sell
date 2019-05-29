from django.conf import settings
from django.db import models


from accounts.models import Profile


class StoreProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=10, unique=True)
    photo = models.ImageField(blank=True)
    comment = models.CharField(max_length=200, blank=True, verbose_name="소개", default="반갑습니다.")
    created_at = models.DateTimeField(auto_now_add=True)

