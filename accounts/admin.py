from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth import get_user_model

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from hitcount.models import HitCount, Hit, BlacklistIP, BlacklistUserAgent

from store.models import StoreProfile, QuestionComment, StoreGrade

from .forms import SignupForm
from .models import UserSession, Profile, ProxyStoreProfile

admin.site.unregister(HitCount)
admin.site.unregister(Hit)
admin.site.unregister(BlacklistIP)
admin.site.unregister(BlacklistUserAgent)
admin.site.register(Permission)


def store_image(obj):

    if type(obj) == get_user_model():
        link = reverse('admin:accounts_proxystoreprofile_change', args=[force_text(obj.storeprofile.pk)])
        return mark_safe('<a href="{link}"><img src="{url}" width="{width}" height={height} /></a>'.format(
            link=link,
            url=obj.storeprofile.photo.url,
            width=100,
            height=100,
        ))
    else:
        link = reverse('admin:accounts_proxystoreprofile_change', args=[force_text(obj.pk)])
        return mark_safe('<a href="{link}"><img src="{url}" width="{width}" height={height} /></a>'.format(
            link=link,
            url=obj.photo.url,
            width=100,
            height=100,
        ))
store_image.short_description = '스토어 사진 뷰'


class QuestionCommentAdmin(admin.StackedInline):
    model = QuestionComment
    extra = 0
    fields = ['author', 'comment', 'updated_at']
    readonly_fields = ['author', 'updated_at']

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class StoreGradeAdmin(admin.StackedInline):
    model = StoreGrade
    extra = 0
    fields = ['store_item', 'rating', 'author', 'grade_comment', 'updated_at']
    readonly_fields = ['store_item', 'rating', 'author', 'updated_at']

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ProfileInline(admin.StackedInline):
    model = Profile

class StoreProfileInline(admin.StackedInline):
    model = StoreProfile
    fields = ['name', store_image, 'photo', 'comment','get_edit_link']
    readonly_fields = [store_image,'get_edit_link']

    def get_edit_link(self, obj=None):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:accounts_proxystoreprofile_change', args=[force_text(obj.pk)])
            return mark_safe("""<a href="{url}">{text}</a>""".format(
                url=url,
                text=("가게 평점, 문의글 보러가기"),
            ))
        return "저장하시고 이용해주세요"
    get_edit_link.short_description = ("가게 자세히 보기")


@admin.register(get_user_model())
class AdminUser(AuthUserAdmin):
    save_on_top = True
    list_display = ('id', store_image,'username','email','user_phone', 'is_active', 'is_staff','item_ctn', 'hit_count')
    list_display_links = ['username']
    list_editable = ('is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'email')
    actions = ('user_acitve','user_disable')
    ordering = ('-is_superuser', '-is_staff', '-is_active')
    list_per_page = 20
    date_hierarchy = 'date_joined'

    inlines = (ProfileInline, StoreProfileInline,)
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


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _item_count=Count("item", distinct=True),
            hit_count_generic = F('storeprofile__hit_count_generic')
        )
        return queryset

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'password', 'email', 'last_login', 'date_joined']
        else:
            return []


    def hit_count(self, obj):
        return obj.storeprofile.hit_count.hits
    hit_count.short_description = '방문수'
    hit_count.admin_order_field = 'hit_count_generic'

    def item_ctn(self, obj):
        return obj._item_count
    item_ctn.short_description = '물품 개수'
    item_ctn.admin_order_field = '_item_count'

    def user_phone(self, obj):
        return obj.profile.phone
    user_phone.short_description = '연락처'

    def user_acitve(self, request, queryset):
        queryset.update(is_active = True)
        # self.message_user(request, 'hello world')
    user_acitve.short_description = '유저 활성화'

    def user_disable(self, request, queryset):
        queryset.update(is_active = False)
    user_disable.short_description = '유저 비활성화'


    def create_storeprofile(self, request, queryset):
        for user in queryset:
            StoreProfile.objects.create(user=user, name=user.username + '의 가게')
    create_storeprofile.short_description = '스토어프로필 만들기'



@admin.register(ProxyStoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['user', 'name', 'hit_count']
    list_display_links = ['user', 'name']
    fields = ['name', store_image, 'photo', 'comment']
    readonly_fields = [store_image]
    inlines = [QuestionCommentAdmin, StoreGradeAdmin]


    def hit_count(self, obj):
        return obj.hit_count.hits
    hit_count.short_description = '방문수'
    hit_count.admin_order_field = 'hit_count_generic'

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserSession)
class Session(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'created_at']
    list_display_links = ['user', 'session_key']
    ordering = ['user']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
