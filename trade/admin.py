from django.contrib import admin

from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe

from category.models import Category
from category.admin import CategoryFilter
from .models import Item, ItemImage, ItemComment, Order


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
    readonly_fields = ['user', 'parent', 'created_at','updated_at']

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
    list_display = ['pk','user','title','desc','amount', 'category', 'item_status','pay_status', 'updated_at']
    list_display_links = ['user','amount', 'title', 'desc']
    # list_editable = ('title', 'desc')
    list_filter = (CategoryItmeFilter,'item_status','pay_status', 'updated_at')
    search_fields = ('title','desc')
    list_per_page = 50
    inlines = [ItemImageAdmin, ItemCommentAdmin]


    readonly_fields = ['user', 'amount', 'category', 'item_status', 'pay_status']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'imp_uid', 'user', 'name', 'amount_html', 'status_html', 'paid_at', 'receipt_link', 'is_active']
    actions = ['do_update', 'do_cancel']

    def do_update(self, request, queryset):
        '주문 정보를 갱신합니다.'
        total = queryset.count()
        if total > 0:
            for order in queryset:
                order.update()
            self.message_user(request, '주문 {}건의 정보를 갱신했습니다.'.format(total))
        else:
            self.message_user(request, '갱신할 주문이 없습니다.')

    do_update.short_description = '선택된 주문들의 아임포트 정보 갱신하기'

    def do_cancel(self, request, queryset):
        '선택된 주문에 대해 결제취소요청을 합니다.'
        queryset = queryset.filter(status='paid')
        total = queryset.count()

        if total > 0:
            for order in queryset:
                order.cancel()
            self.message_user(request, '주문 {}건을 취소했습니다.'.format(total))
        else:
            self.message_user(request, '취소할 주문이 없습니다.')

    do_cancel.short_description = '선택된 주문에 대해 결제취소요청하기'
