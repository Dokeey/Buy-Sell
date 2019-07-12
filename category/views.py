from operator import attrgetter

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from .models import Category
from trade.models import Item


# def categories(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     parent_category = category.get_ancestors()
#     categories_items = []
#
#     for item in category.item_set.all():
#         categories_items.append(item)
#
#     for children in category.get_children():
#         for item in children.item_set.all():
#             categories_items.append(item)
#
#     categories_items = sorted(categories_items, key=attrgetter('created_at'))
#
#     return render(request, 'category/categories.html', {
#         'category': category,
#         'parent_category': parent_category,
#         'categories_items': categories_items,
#     })

class SearchItemList(ListView):
    model = Item
    template_name = 'category/search_item.html'
    context_object_name = 'items'
    ordering = '-created_at'
    paginate_by = 20

    def get_queryset(self):
        self.query = self.request.GET.get('query','')
        qs = super().get_queryset()

        if self.query:
            qs = qs.filter(title__icontains=self.query)

        return qs

    def get_ordering(self):
        ordering = self.request.GET.get('sort','-created_at')

        if ordering == 'looks':
            ordering = 'hit_count_generic'
        elif ordering == 'hprice':
            ordering = '-amount'
        elif ordering == 'lprice':
            ordering = 'amount'

        return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5  # Display only 5 page numbers
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        context['sort'] = self.request.GET.get('sort','-created_at')
        context['item_ctn'] = self.get_queryset().count()
        if self.query:
            context['query'] = self.query

        return context



class CategoryItemList(SearchItemList):
    template_name = 'category/category_item.html'


    def get_queryset(self):
        category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        categories_items = []
        for item in category.item_set.all():
            categories_items.append(item.id)

        for children in category.get_children():
            for item in children.item_set.all():
                categories_items.append(item.id)

        self.queryset = Item.objects.filter(id__in=categories_items)

        return super().get_queryset()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, pk=self.kwargs.get('pk'))

        context['category'] = category
        context['parent_category'] = category.get_ancestors()

        return context