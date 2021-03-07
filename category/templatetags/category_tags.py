import itertools

from django import template
from trade.models import Item
from ..models import Category

register = template.Library()


@register.simple_tag
def category_menu():
    categories = Category.objects.all()
    return categories


@register.simple_tag
def child_category_items(category):
    category_list = category.get_descendants(include_self=True)

    items = Item.objects.prefetch_related('itemimage_set').all()
    items = items.filter(category__in=category_list)[:12]

    return items


@register.simple_tag
def item_first_image(item):
    return item.itemimage_set.all()[0].photo


@register.simple_tag
def div(value, num):
    result = int(value / num)
    return result
