from operator import attrgetter

from django.shortcuts import render, get_object_or_404
from .models import Category


def categories(request, pk):
    category = get_object_or_404(Category, pk=pk)
    parent_category = category.get_ancestors()
    categories_items = []

    for item in category.item_set.all():
        categories_items.append(item)

    for children in category.get_children():
        for item in children.item_set.all():
            categories_items.append(item)

    categories_items = sorted(categories_items, key=attrgetter('created_at'))

    return render(request, 'category/categories.html', {
        'category': category,
        'parent_category': parent_category,
        'categories_items': categories_items,
    })
