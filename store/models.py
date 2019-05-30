from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from accounts.models import Profile


class StoreProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=10, unique=True)
    photo = ProcessedImageField(
        blank=True,
        upload_to='profile/storephoto',
        processors=[ResizeToFill(100,100)],
        format='PNG',
        options={'quality': 60}

    )
    comment = models.CharField(max_length=200, blank=True, verbose_name="소개", default="반갑습니다.")
    created_at = models.DateTimeField(auto_now_add=True)

