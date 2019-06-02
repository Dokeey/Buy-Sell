from django.contrib import admin

from .models import StoreProfile, QuestionComment


@admin.register(StoreProfile)
class StoreProfile(admin.ModelAdmin):
	list_display=['user','name']

@admin.register(QuestionComment)
class Comment(admin.ModelAdmin):
	list_display = ['store_profile','author']