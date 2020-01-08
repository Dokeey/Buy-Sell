from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    name = models.CharField(verbose_name="카테고리 명", max_length=50, unique=True)
    parent = TreeForeignKey('self', verbose_name="상위 카테고리", on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name