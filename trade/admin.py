from django.contrib import admin

# Register your models here.
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['user','title','desc','amount','photo','category','sub_category','status','is_public','created_at','updated_at']