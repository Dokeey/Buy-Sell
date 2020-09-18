from category.models import Category
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, F
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

from .models import Item, ItemImage, ItemComment, ProxyCategory, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ("name",)


class InlineItemAdmin(admin.StackedInline):
    model = Item
    extra = 0

    fields = ('user', 'title', 'desc', 'item_photos', 'get_edit_link')
    readonly_fields = ['user', 'item_photos', 'get_edit_link']

    def item_photos(self, obj=None):
        imageset = obj.itemimage_set.all()
        html = ''
        for image in imageset:
            ht = '<a href="{url}" style="padding:10px"><img style="border:1px solid #999999;" src="{url}" width="{width}" height={height} /></a>'.format(
                url=image.photo.url,
                width=100,
                height=100,
            )
            html = html + ht
        return mark_safe(html)

    item_photos.short_description = ("사진 자세히 보기")

    def get_edit_link(self, obj=None):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[force_text(obj.pk)])
            return mark_safe("""<a href="{url}">{text}</a>""".format(
                url=url,
                text=("물품 상세 정보, 문의글 보러가기"),
            ))
        return "저장하시고 이용해주세요"

    get_edit_link.short_description = ("물품 자세히 보기")

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CategoryFilter(SimpleListFilter):
    title = '최상위 카테고리'
    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        roots = Category.objects.root_nodes()
        return [(root.id, root) for root in roots]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.get(id=self.value()).get_descendants(include_self=True).annotate(_item_ctn=Count("item"))
        else:
            return queryset


@admin.register(ProxyCategory)
class CategoryAdmin(DraggableMPTTAdmin):
    # specify pixel amount for this ModelAdmin only:

    list_display = ('tree_actions', 'indented_title', 'item_count')  # Sane defaults.
    list_display_links = ('indented_title',)  # Sane defaults.
    inlines = [InlineItemAdmin]
    list_filter = (CategoryFilter,)

    # ordering = ['indented_title']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _item_ctn=Count("item"),
            # parent=
        )
        return qs

    def item_count(self, obj):
        return obj.item_set.all().count()

    item_count.short_description = '물품 개수'
    item_count.admin_order_field = '_item_ctn'


class ItemImageAdmin(admin.TabularInline):
    model = ItemImage
    extra = 0
    max_num = 5

    readonly_fields = ['item_iamge']

    def item_iamge(self, obj=None):
        return mark_safe('<a href="{url}"><img src="{url}" width="{width}" height={height} /></a>'.format(
            url=obj.photo.url,
            width=100,
            height=100,
        ))

    item_iamge.short_description = ("사진 자세히 보기")

    def has_delete_permission(self, request, obj=None):
        return False


class ItemCommentAdmin(admin.StackedInline):
    model = ItemComment
    extra = 0
    ordering = ['parent']
    fields = ['user', 'parent', 'message', 'updated_at']
    readonly_fields = ['user', 'parent', 'created_at', 'updated_at']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CategoryItmeFilter(CategoryFilter):
    def queryset(self, request, queryset):
        if self.value():
            category = get_object_or_404(Category, pk=self.value())
            categories_items = []

            for cate in category.get_descendants(include_self=True):
                [categories_items.append(item.id) for item in cate.item_set.all()]

            queryset = Item.objects.filter(id__in=categories_items)

            return queryset
        else:
            return queryset


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['hit_count', 'get_wishlist_count', 'pk', 'user', 'title', 'desc', 'amount', 'category',
                    'item_status', 'pay_status', 'updated_at']
    list_display_links = ['user', 'amount', 'title', 'desc']
    # list_editable = ('title', 'desc')
    list_filter = (CategoryItmeFilter, 'item_status', 'pay_status', 'updated_at')
    search_fields = ('_username', 'title', 'desc')
    list_per_page = 50
    inlines = [ItemImageAdmin, ItemCommentAdmin]
    date_hierarchy = 'created_at'

    readonly_fields = ['hit_count', 'get_wishlist_count', 'get_user_link', 'amount', 'category', 'item_status',
                       'pay_status']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _username=F('user__username'),
        )
        return qs

    def get_user_link(self, obj):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:accounts_user_change', args=[force_text(obj.user.pk)])
            return mark_safe("""<a href="{url}">{text}</a>""".format(
                url=url,
                text=obj.user,
            ))
        return obj.user

    get_user_link.short_description = ("물품 주인")

    def hit_count(self, obj):
        return obj.hit_count.hits

    hit_count.short_description = '조회수'
    hit_count.admin_order_field = 'hit_count_generic'

    def get_wishlist_count(self, obj):
        return obj.wishlist_set.all().count()

    get_wishlist_count.short_description = '찜한 횟수'

    def has_add_permission(self, request, obj=None):
        return False
