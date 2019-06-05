from django import template
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from store.models import StoreProfile, StoreGrade, QuestionComment
from trade.models import Item

register = template.Library()

@register.simple_tag
def store_rating(pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    grades = StoreGrade.objects.filter(store_profile_id=stores.pk)
    rates = grades.count()
    sum = grades.aggregate(Sum('rating'))['rating__sum']
    if rates:
        end = round((sum / rates), 1)
    else:
        end = 0
    return end

@register.simple_tag
def store_item_list(pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    item_count = Item.objects.filter(user_id=stores.user_id).count()
    return item_count


@register.simple_tag
def store_grade_list(pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    grade_count = StoreGrade.objects.filter(store_profile_id=stores.pk).count()
    return grade_count

@register.simple_tag
def store_question_list(pk):
    stores = get_object_or_404(StoreProfile, pk=pk)
    question_count = QuestionComment.objects.filter(store_profile_id=stores.pk).count()
    return question_count