from random import randrange

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from hitcount.models import HitCountMixin, HitCount
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill
from django_cleanup import cleanup


def get_random():
    rand = randrange(1,10)
    return 'profile/default/{}.png'.format(rand)

@cleanup.ignore
class StoreProfile(models.Model, HitCountMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="유저", on_delete=models.CASCADE)
    name = models.CharField(max_length=20, verbose_name="가게명", unique=True)
    photo = ProcessedImageField(
        verbose_name="가게 사진",
        null=True,
        default=get_random,
        upload_to='profile/storephoto',
        processors=[ResizeToFill(200, 200)],
        format='PNG',
        options={'quality': 60}

    )
    comment = models.TextField(max_length=200, blank=True, verbose_name="소개", default="반갑습니다.")
    created_at = models.DateTimeField(verbose_name="생성일", auto_now_add=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "가게"
        verbose_name_plural = "가게"

from django.contrib.auth import get_user_model
User = get_user_model()
user_id = User.objects.get(username='deleteuser').pk

class QuestionComment(models.Model):
    store_profile = models.ForeignKey(StoreProfile, verbose_name="가게", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="작성자", on_delete=models.SET_DEFAULT,default=user_id)
    comment = models.TextField(verbose_name="문의글", max_length=1000)
    created_at = models.DateTimeField(verbose_name="작성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)

    parent = models.ForeignKey('self', verbose_name="상위 댓글", null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return self.author.storeprofile.name

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "가게 문의"
        verbose_name_plural = "가게 문의"


from trade.models import Item


class StoreGrade(models.Model):
    store_profile = models.ForeignKey(StoreProfile, verbose_name="가게", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="작성자", on_delete=models.SET_DEFAULT,default=user_id)
    store_item = models.ForeignKey(Item, verbose_name="구매한 물품", on_delete=models.SET_NULL, null=True)
    grade_comment = models.TextField(verbose_name="물품평", max_length=250)
    rating = models.PositiveIntegerField(
        verbose_name="점수",
        choices=(
            (1, '★☆☆☆☆'),
            (2, '★★☆☆☆'),
            (3, '★★★☆☆'),
            (4, '★★★★☆'),
            (5, '★★★★★')
        ),
        default=0,
        db_index=True
    )
    created_at = models.DateTimeField(verbose_name="작성일", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="최근 업데이트", auto_now=True)

    def __str__(self):
        return self.author.storeprofile.name

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "가게 평점"
        verbose_name_plural = "가게 평점"