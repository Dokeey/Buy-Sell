from django.contrib import admin

# Register your models here.

from .models import CustomerFAQ, CustomerAsk, CustomerCategory, CustomerNotice


@admin.register(CustomerFAQ)
class CustomerFAQAdmin(admin.ModelAdmin):
    list_display = [ 'faq_title']

@admin.register(CustomerAsk)
class CustomerAskAdmin(admin.ModelAdmin):
    list_display = ['ask_title', 'ask_going']

@admin.register(CustomerCategory)
class CustomerCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']

@admin.register(CustomerNotice)
class CustomerNoticeAdmin(admin.ModelAdmin):
    list_display = ['pk','notice_title','created_at']