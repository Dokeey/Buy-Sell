from django.contrib import admin
from .models import Category, SubCategory

# Register your models here.

@admin.register(Category)
class ProfileAdmin(admin.ModelAdmin):
	list_display=['name']


@admin.register(SubCategory)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('get_category','name')

    def get_category(self,obj):
        return obj.category.name

    get_category.short_description = '상위 카테고리'
