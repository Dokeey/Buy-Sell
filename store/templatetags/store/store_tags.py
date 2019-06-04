from django import template

from store.models import StoreProfile

register = template.Library()

@register.simple_tag
def store_profile():
    sprofile = StoreProfile.objects.all()

    return sprofile