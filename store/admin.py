from django.contrib import admin

from .models import StoreProfile


@admin.register(StoreProfile)
class StoreProfile(admin.ModelAdmin):
	list_display=['user','name']