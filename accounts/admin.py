from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth import get_user_model

from django.contrib.auth.models import Permission
from django.db.models import Count
from django.utils.safestring import mark_safe

from store.models import StoreProfile

from .forms import SignupForm
from .models import UserSession, Profile

admin.site.register(Permission)

class ProfileInline(admin.StackedInline):
    model = Profile

class StoreProfileInline(admin.StackedInline):
    model = StoreProfile
    readonly_fields = ['store_image']

    def store_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.photo.url,
            width=100,
            height=100,
            )
    )
    store_image.short_description = '스토어 사진 뷰'

@admin.register(get_user_model())
class AdminUser(AuthUserAdmin):

    list_display = ('id', 'store_image','username','email','user_phone', 'is_active', 'is_staff','item_ctn')
    list_display_links = ['username']
    list_editable = ('is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'email')
    actions = ('user_acitve','create_storeprofile')
    ordering = ('-is_superuser', '-is_staff', '-is_active')
    list_per_page = 20

    inlines = (ProfileInline, StoreProfileInline)
    fieldsets = (
        # (('유저 프로필과 가게 프로필'),{'fields':(inlines)}),
        (('개인 정보'), {'fields': ('username', 'email')}),
        (('그룹과 권한'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('시간 정보'), {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _item_count=Count("item", distinct=True),
        )
        return queryset

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'email', 'last_login', 'date_joined']
        else:
            return []

    def store_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.storeprofile.photo.url,
            width=100,
            height=100,
            )
    )
    store_image.short_description = '스토어 사진 뷰'


    def item_ctn(self, obj):
        return obj._item_count
    item_ctn.short_description = '물품 개수'
    item_ctn.admin_order_field = '_item_count'

    def user_phone(self, obj):
        return obj.profile.phone
    user_phone.short_description = '연락처'

    def user_acitve(self, request, queryset):
        for user in queryset:
            user.is_active = True
            user.save()
        # self.message_user(request, 'hello world')
    user_acitve.short_description = '유저 활성화하기'


    def create_storeprofile(self, request, queryset):
        from store.models import StoreProfile
        for user in queryset:
            StoreProfile.objects.create(user=user, name=user.username + '의 가게')
    create_storeprofile.short_description = '스토어프로필 만들기'


@admin.register(UserSession)
class Session(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'created_at']

