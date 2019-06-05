from django.contrib import admin

# Register your models here.
from .models import Item, ItemComment, Order

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['user','title','desc','amount','photo','category', 'item_status','pay_status','created_at','updated_at']


@admin.register(ItemComment)
class ItemCommentAdmin(admin.ModelAdmin):
    list_display = ['parent', 'message', 'item', 'secret','created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['imp_uid', 'user', 'name', 'amount_html', 'status_html', 'paid_at', 'receipt_link']
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
