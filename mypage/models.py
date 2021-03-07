from django.conf import settings
from django.db import models

from trade.models import Item, Order


class WishList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="사용자", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, verbose_name="물품", on_delete=models.CASCADE)

    class Meta:
        ordering = ('-id',)
        verbose_name = "찜 목록"
        verbose_name_plural = "찜 목록"

    def __str__(self):
        return self.item.title


class ProxyOrder(Order):
    class Meta:
        proxy = True
        ordering = ('-id',)
        verbose_name = "거래 내역"
        verbose_name_plural = "거래 내역"


from store.models import StoreProfile


class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="사용자", on_delete=models.CASCADE)
    store = models.ForeignKey(StoreProfile, verbose_name="가게", on_delete=models.CASCADE)

    class Meta:
        ordering = ('-id',)
        verbose_name = "팔로우"
        verbose_name_plural = "팔로우"

    def __str__(self):
        return self.store.name
