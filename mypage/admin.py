from django.contrib import admin

# Register your models here.
from .models import WishList


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ['id','user','item']