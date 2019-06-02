from django.conf import settings
from django.db import models
from category.models import Category, SubCategory

# Create your models here.
# from imagekit.generatorlibrary import Thumbnail
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill


class Item(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    desc = models.TextField(blank=True)
    amount = models.PositiveIntegerField()
    photo = ProcessedImageField(
            upload_to = 'blog/post',
            processors = [ResizeToFill(100, 100)], # 처리할 작업 목룍
            format = 'PNG',					# 최종 저장 포맷
            options = {'quality': 60}
        )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ItemComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    message = models.TextField()
    secret = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='replies')

    class Meta:
        # sort comments in chronological order by default
        ordering = ('-created_at',)