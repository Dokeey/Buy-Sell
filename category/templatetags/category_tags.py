from django import template
from ..models import Category, SubCategory

register = template.Library()

@register.simple_tag
def category_menu():
    cates = Category.objects.all()
    return cates

@register.simple_tag
def subcategory_menu():
    subcates = SubCategory.objects.all()
    return subcates

@register.simple_tag
def subcate(category):
    subcates = SubCategory.objects.filter(category=category)
    return subcates