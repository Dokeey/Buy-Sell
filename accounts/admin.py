from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth import get_user_model


# Register your models here.
from .models import UserSession, Profile


@admin.register(get_user_model())
class AdminUser(AuthUserAdmin):
    # list_display = ('username', 'email', 'nick_name', 'phone', 'address', 'account_num', 'is_active')
    list_display = ('id','username', 'email', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    actions = ['유저_활성화하기','유저_스토어프로필_만들기']

    def 유저_활성화하기(self, request, queryset):
        for user in queryset:
            user.is_active = True
            user.save()
        # self.message_user(request, 'hello world')

    def 유저_스토어프로필_만들기(self, request, queryset):
        from store.models import StoreProfile
        for user in queryset:
            StoreProfile.objects.create(user=user, name=user.profile.nick_name + '의 가게')


@admin.register(UserSession)
class Session(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'created_at']


@admin.register(Profile)
class AdminProfile(admin.ModelAdmin):
    list_display = ('user', 'email', 'nick_name', 'phone', 'post_code','address', 'detail_address','account_num')