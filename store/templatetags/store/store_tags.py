from django import template
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from store.models import StoreProfile, StoreGrade, QuestionComment
from trade.models import Item, Order

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
    order = Item.objects.filter(user=stores.user, pay_status='sale_complete').count()
    return order

@register.simple_tag
def store_ident(user_id):
    return StoreProfile.objects.get(user_id=user_id).pk
