from django.contrib import admin

# Register your models here.

from .models import CustomerFAQ, CustomerAsk, CustomerCategory


@admin.register(CustomerFAQ)
class CustomerFAQForm(admin.ModelAdmin):
    list_display = [ 'faq_title']

@admin.register(CustomerAsk)
class CustomerAskForm(admin.ModelAdmin):
    list_display = ['ask_title']

@admin.register(CustomerCategory)
class CustomerCategoryForm(admin.ModelAdmin):
    list_display = ['pk', 'customer_category']