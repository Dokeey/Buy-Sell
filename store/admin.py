from django.contrib import admin

from .models import QuestionComment, StoreGrade


# @admin.register(QuestionComment)
# class CommentAdmin(admin.ModelAdmin):
# 	list_display = ['pk', 'parent_id', 'store_profile', 'author']
#
# @admin.register(StoreGrade)
# class StoreGradeAdmin(admin.ModelAdmin):
# 	list_display = ['pk', 'author', 'rating']