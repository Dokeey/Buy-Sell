from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Category

# Register your models here.

class CategoryAdmin(DraggableMPTTAdmin):
    # specify pixel amount for this ModelAdmin only:
    mptt_level_indent = 20

admin.site.register(Category, CategoryAdmin)

