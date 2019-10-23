from django.contrib import admin

# Register your models here.
from django_summernote.admin import SummernoteModelAdmin

from .models import CustomerFAQ, CustomerAsk, CustomerCategory, CustomerNotice


@admin.register(CustomerFAQ)
class CustomerFAQAdmin(SummernoteModelAdmin):
    list_display = [ 'faq_category' , 'faq_title']
    summernote_fields = '__all__'

@admin.register(CustomerAsk)
class CustomerAskAdmin(SummernoteModelAdmin):
    list_display = ['ask_title', 'ask_going']
    summernote_fields = '__all__'

@admin.register(CustomerCategory)
class CustomerCategoryAdmin(admin.ModelAdmin):
    list_display = ['pk','name', 'parent']

@admin.register(CustomerNotice)
class CustomerNoticeAdmin(SummernoteModelAdmin):
    list_display = ['pk','notice_title','created_at']
    summernote_fields = '__all__'