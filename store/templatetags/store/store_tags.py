from django import template
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from store.models import StoreProfile, StoreGrade, QuestionComment
from trade.models import Item, Order
from django import template

register = template.Library()

@register.simple_tag
def store_rating(pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    grades = StoreGrade.objects.filter(store_profile_id=stores.pk)
    rates = grades.count()
    if rates:
        sum = grades.aggregate(Sum('rating'))['rating__sum']
        end = round((sum / rates), 1)
    else:
        end = 0
    return end

@register.simple_tag
def store_sell_list(pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    # order = Item.objects.filter(user=stores.user, pay_status='sale_complete').count()
    orders = Item.objects.filter(user=stores.user)
    items = []
    for order in orders:
        item = len(order.order_set.filter(status='success'))
        if item == 1:
            items.append(item)
    order = len(items)

    return order

@register.simple_tag
def store_rating_percent(pk,ra):
    #그평점/전체
    grades = StoreGrade.objects.filter(store_profile_id=pk)
    rates = grades.count()
    part_rates = grades.filter(rating=ra).count()
    if part_rates:
        rate= round(((part_rates/rates)*100),1)
    else:
        rate = 0
    return rate
