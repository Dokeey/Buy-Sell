from operator import attrgetter

from django.contrib import messages
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
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
class BaseItemList(ListView):
    model = Item
    context_object_name = 'items'
    ordering = '-created_at'
    paginate_by = 24


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
        context['prev'] = start_index - 4
        context['next'] = end_index + 1
        context['last_page'] = max_index
        context['page_range'] = page_range

        context['sort'] = self.request.GET.get('sort','-created_at')
        context['item_ctn'] = self.get_queryset().count()

        return context



class SearchItemList(BaseItemList):
    template_name = 'category/search_item.html'

    def get_queryset(self):
        self.query = self.request.GET.get('query','')
        self.cate = self.request.GET.get('cate','')
        self.qs = super().get_queryset()

        if self.query == '':
            messages.error(self.request, '잘못된 접근 입니다.')
            url = self.request.GET.get('next') or 'root'
            redirect(url)

        if self.query:
            self.qs = self.qs.filter(Q(title__icontains=self.query) | Q(desc__icontains=self.query)).distinct()

        if self.cate:
            category = get_object_or_404(Category, id=self.cate)
            self.qs = self.qs.filter(category=category)

        return self.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_category'] = self.qs.values('category__name','category__id').annotate(category_count = Count('id')).order_by('category')

        context['query'] = self.query
        context['cate'] = self.cate

        return context



class CategoryItemList(BaseItemList):
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