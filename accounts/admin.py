from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth import get_user_model


# Register your models here.
from .models import UserSession


@admin.register(get_user_model())
class AdminUser(AuthUserAdmin):
    list_display = ('username', 'email', 'nick_name', 'phone', 'address', 'account_num', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    actions = ['마케팅_이메일보내기']

    def 마케팅_이메일보내기(self, request, queryset):
        for user in queryset:
            pass
        self.message_user(request, 'hello world')


@admin.register(UserSession)
class Session(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'created_at']