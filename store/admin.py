from django.contrib import admin

from store.models import StoreProfile


@admin.register(StoreProfile)
class StoreProfile(admin.ModelAdmin):
	list_display=['user','name']