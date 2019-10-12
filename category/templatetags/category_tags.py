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
    categories_items = []
    for item in category.item_set.all():
        categories_items.append(item.id)

    for children in category.get_children():
        for item in children.item_set.all():
            categories_items.append(item.id)

    items = Item.objects.filter(id__in=categories_items)
    return items


@register.simple_tag
def div(value, num):
    result = int(value/num)
    return result