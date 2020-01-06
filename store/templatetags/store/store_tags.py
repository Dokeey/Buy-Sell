
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Count,F
from django.shortcuts import get_object_or_404
from hitcount.models import HitCount
from rank import DenseRank

from mypage.models import Follow
from store.models import StoreProfile, StoreGrade
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
    order=0
    search_sell = Order.objects.filter(status='success').values('item__user')
    if not search_sell:
        order = 0
    else:
        order1 =  Order.objects.filter(status='success').values('item__user').annotate(count=Count('item__user')).order_by('count')
        for orders in order1:
            if orders['item__user'] == pk :
                order = orders['count']
    # stores = get_object_or_404(StoreProfile, pk=pk)
    # orders = Item.objects.filter(user=stores.user)
    # items = []
    # for order in orders:
    #     item = len(order.order_set.filter(status='success'))
    #     if item == 1:
    #         items.append(item)
    # order = len(items)

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


# star_grade 전역 변수
ctype = ContentType.objects.get_for_model(StoreProfile)
search_grade = StoreGrade.objects.values('store_profile').annotate(rating_sum=Sum('rating') / Count('rating'),
                                                                   count=Count('rating'),
                                                                   rank=DenseRank('rating_sum', 'count')).order_by('-rating_sum', '-count')
search_hit = HitCount.objects.filter(content_type=ctype).values('object_pk').annotate(rank=DenseRank('hits'))
search_sell = Order.objects.filter(status='success').values('item__user').annotate(count = Count('status'), rank=DenseRank('count')).order_by('user')
search_follow = Follow.objects.values('store').annotate(foll_count=Count('store'),rank=DenseRank('foll_count')).order_by('-foll_count')
@register.simple_tag
def star_grade(pk):
    context={}
    #hit rank
    for i in search_hit:
        if i['object_pk'] == pk.pk:
            context['hit_rank'] = i['rank']

    #follow_rank
    context['follow_rank'] = ''
    for i in search_follow:
        if i['store'] == pk.pk:
            context['follow_rank'] = i['rank']
    if context['follow_rank'] == '':
        context['follow_rank'] = '-'
    #sell rank
    context['sell_rank'] = ''
    for i in search_sell:
        if i['item__user'] == pk.user.pk:
            context['sell_rank'] = i['rank']

    if context['sell_rank'] == '':
        context['sell_rank'] = '-'

    #grade rank
    context['grade_rank'] = ''
    for i in search_grade :
        if i['store_profile'] == pk.pk:
             context['grade_rank'] = i['rank']
    if context['grade_rank'] == '':
        context['grade_rank'] = '-'
    return context
