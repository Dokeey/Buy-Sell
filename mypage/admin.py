from django.contrib import admin
from django.db.models import F
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from .models import WishList, Follow, ProxyOrder


@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ['id','user','item']


    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id','user','store']


    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(ProxyOrder)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'sell_user', 'pay_choice', 'item', 'amount_html', 'status_html', 'updated_at']
    list_display_links = ['pay_choice', 'item']
    list_filter = ('status', 'pay_choice', 'updated_at')
    search_fields = ('_sell_user', '_user', '_item')
    date_hierarchy = 'created_at'
    actions = ['do_cancel']

    # fieldsets = (
    #     # (('유저 프로필과 가게 프로필'),{'fields':(inlines)}),
    #     (('물품 정보'), {'fields': ('id', 'item', 'sell_user')}),
    #     (('구매자 정보'), {'fields': ('user', 'email', 'username', 'phone', 'post_code', 'address', 'detail_address', 'requirement')}),
    #     (('결제 정보'), {'fields': ('pay_choice', 'amount_html', 'status_html', 'updated_at')}),
    # )
    # fields          = ['id', 'user', 'email', 'username', 'phone', 'post_code', 'address', 'detail_address', 'requirement', 'sell_user', 'pay_choice', 'item', 'amount_html', 'status_html', 'updated_at', ]
    readonly_fields = ['id', 'get_user_link','get_item_image', 'get_hit_count', 'email', 'username', 'phone', 'post_code', 'address', 'detail_address', 'requirement', 'get_sell_user_link', 'pay_choice', 'get_item_link', 'amount_html', 'status_html', 'updated_at', ]


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _user=F('user__username'),
            _item=F('item__title'),
            _sell_user=F('item__user__username'),
        )
        return qs

    def get_fieldsets(self, request, obj=None):
        self.fieldsets = [
            # (('유저 프로필과 가게 프로필'),{'fields':(inlines)}),
            (('물품 정보'), {'fields': ('id', 'get_sell_user_link', 'get_item_link', 'get_hit_count', 'get_item_image')}),
            (('구매자 정보'), {'fields': (
            'get_user_link', 'email', 'username', 'phone', 'post_code', 'address', 'detail_address', 'requirement')}),
            (('결제 정보'), {'fields': ('pay_choice', 'amount_html', 'status_html', 'updated_at')}),
        ]
        if obj.pay_choice == 'import':
            field = (('이니페이 결제 정보'), {'fields': ('imp_uid','receipt_link', 'cancel_reason', 'fail_reason', 'paid_at', 'failed_at', 'cancelled_at')})
            # self.fieldsets[2][1]['fields'] = list(self.fieldsets[2][1]['fields']) + ['imp_uid','receipt_link', 'cancel_reason', 'fail_reason', 'paid_at', 'failed_at', 'cancelled_at']
        else:
            field = (('계좌이체 결제 정보'), {'fields': ('is_active',)})
            # self.fieldsets[2][1]['fields'] = list(self.fieldsets[2][1]['fields']) + ['is_active', ]
        self.fieldsets.append(field)
        return tuple(self.fieldsets)

    # def get_fields(self, request, obj=None):
    #     if obj.pay_choice == 'import':
    #         return self.fields + ['imp_uid','receipt_link', 'cancel_reason', 'fail_reason', 'paid_at', 'failed_at', 'cancelled_at']
    #     else:
    #         return self.fields + ['is_active', ]
    #
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + list(self.fieldsets[3][1]['fields'])


    def get_item_link(self, obj):
        url = reverse('admin:trade_item_change', args=[force_text(obj.item.pk)])
        return mark_safe("""<a href="{url}">{text}</a>""".format(
            url=url,
            text=obj.item,
        ))
    get_item_link.short_description = ("물품 자세히 보기")


    def get_sell_user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[force_text(obj.item.user.pk)])
        return mark_safe("""<a href="{url}">{text}</a>""".format(
            url=url,
            text=obj.item.user,
        ))
    get_sell_user_link.short_description = ("판매자 자세히 보기")


    def get_user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[force_text(obj.user.pk)])
        return mark_safe("""<a href="{url}">{text}</a>""".format(
            url=url,
            text=obj.user,
        ))
    get_user_link.short_description = ("구매자 자세히 보기")

    def get_item_image(self, obj):
        imageset = obj.item.itemimage_set.all()
        html = ''
        for image in imageset:
            ht = '<a href="{url}" style="padding:10px"><img style="border:1px solid #999999;" src="{url}" width="{width}" height={height} /></a>'.format(
                url=image.photo.url,
                width=100,
                height=100,
            )
            html = html + ht
        return mark_safe(html)
    get_item_image.short_description = ("사진 자세히 보기")

    def get_hit_count(self, obj):
        return obj.item.hit_count.hits
    get_hit_count.short_description = '조회수'


    def amount_html(self, obj):
        return obj.amount_html
    amount_html.short_description = '결제 금액'
    amount_html.admin_order_field = 'amount'


    def sell_user(self, obj):
        return obj._sell_user
    sell_user.short_description = '판매자'
    sell_user.admin_order_field = '_sell_user'

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


    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
