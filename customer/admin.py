from django.contrib import admin

# Register your models here.
from django_summernote.admin import SummernoteModelAdmin
from mptt.admin import DraggableMPTTAdmin

from .models import CustomerFAQ, CustomerAsk, CustomerCategory, CustomerNotice
from django_summernote.utils import get_attachment_model

admin.site.unregister(get_attachment_model())


@admin.register(CustomerFAQ)
class CustomerFAQAdmin(SummernoteModelAdmin):
    save_on_top = True
    list_display = ['pk', 'faq_category', 'faq_title']
    list_display_links = ['pk']
    list_editable = ('faq_category', 'faq_title')
    list_filter = ('faq_category', 'updated_at')
    search_fields = ('faq_title',)
    summernote_fields = '__all__'


@admin.register(CustomerAsk)
class CustomerAskAdmin(SummernoteModelAdmin):
    save_on_top = True
    list_display = ['ask_category', 'ask_title', 'ask_going']
    list_display_links = ['ask_title']
    list_editable = ('ask_going',)
    list_filter = ('ask_category', 'ask_going', 'updated_at')
    search_fields = ('ask_title',)
    summernote_fields = '__all__'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CustomerCategory)
class CustomerCategoryAdmin(DraggableMPTTAdmin):
    save_on_top = True
    list_display = ('tree_actions', 'indented_title')  # Sane defaults.
    list_display_links = ('indented_title',)


@admin.register(CustomerNotice)
class CustomerNoticeAdmin(SummernoteModelAdmin):
    save_on_top = True
    list_display = ['pk', 'notice_title', 'updated_at']
    list_display_links = ['pk']
    list_editable = ('notice_title',)
    list_filter = ('updated_at',)
    search_fields = ('notice_title',)
    summernote_fields = '__all__'
