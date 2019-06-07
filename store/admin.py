from django.contrib import admin

from .models import StoreProfile, QuestionComment, StoreGrade


@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
	list_display=['user','name']

@admin.register(QuestionComment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ['store_profile','author']

@admin.register(StoreGrade)
class StoreGradeAdmin(admin.ModelAdmin):
	list_display = ['pk', 'author', 'rating']