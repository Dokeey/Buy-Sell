from random import randrange

from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from trade.models import Item


def get_random():
    rand = randrange(1,10)
    return 'profile/default/{}.png'.format(rand)

class StoreProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, unique=True)
    photo = ProcessedImageField(
        null=True,
        default=get_random,
        upload_to='profile/storephoto',
        processors=[ResizeToFill(100,100)],
        format='PNG',
        options={'quality': 60}

    )
    comment = models.CharField(max_length=200, blank=True, verbose_name="소개", default="반갑습니다.")
    created_at = models.DateTimeField(auto_now_add=True)




class QuestionComment(models.Model):
    store_profile = models.ForeignKey(StoreProfile, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)


class StoreGrade(models.Model):
    store_profile = models.ForeignKey(StoreProfile, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    store_item = models.ForeignKey(Item, on_delete=models.PROTECT)
    grade_comment = models.TextField()
    rating = models.PositiveIntegerField(
        choices=(
            (0, '☆☆☆☆☆'),
            (1, '★☆☆☆☆'),
            (2, '★★☆☆☆'),
            (3, '★★★☆☆'),
            (4, '★★★★☆'),
            (5, '★★★★★')
        ),
        default=0,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)