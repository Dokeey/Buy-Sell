from operator import attrgetter

from django.contrib import messages
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from .models import Category
from trade.models import Item


class BaseItemList(ListView):
    model = Item
    context_object_name = 'items'
    paginate_by = 24

    def get_ordering(self):
        ordering = self.request.GET.get('sort', '-created_at')

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

        context['sort'] = self.request.GET.get('sort', '-created_at')
        context['item_ctn'] = paginator.count

        return context


class SearchItemList(BaseItemList):
    template_name = 'category/search_item.html'

    def get(self, request, *args, **kwargs):
        self.query = self.request.GET.get('query', '').strip()

        if self.query.replace(' ', '') == '':
            self.query = ''

        if self.query == '':
            messages.info(self.request, '검색어를 입력해주세요')
            url = self.request.GET.get('next') or 'root'
            return redirect(url)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.cate = self.request.GET.get('cate', '')
        self.qs = super().get_queryset()
        self.qs = self.qs.prefetch_related("user__storeprofile")
        self.qs = self.qs.prefetch_related("itemimage_set")

        if self.query:
            self.qs = self.qs.filter(Q(title__icontains=self.query) | Q(desc__icontains=self.query))

        if self.cate:
            category = get_object_or_404(Category, id=self.cate)
            self.qs = self.qs.filter(category=category)

        return self.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_category'] = self.qs.values('category__name', 'category__id').annotate(
            category_count=Count('id')).order_by('category__parent')

        context['query'] = self.query
        context['cate'] = self.cate

        return context


class CategoryItemList(BaseItemList):
    template_name = 'category/category_item.html'

    def get(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self):
        self.flag = self.request.GET.get('parent', '')

        items = Item.objects.prefetch_related("user__storeprofile")
        items = items.prefetch_related("itemimage_set")
        if self.flag:
            self.queryset = items.filter(category=self.category)
            return super().get_queryset()

        self.category_list = self.category.get_descendants(include_self=True)
        self.queryset = items.filter(category__in=self.category_list)

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = Item.objects.filter(category__in=self.category.get_descendants())
        categories = categories.values("category").annotate(cnt=Count('*'))
        context['children'] = categories.values_list('category', 'category__name', 'cnt')
        context['category'] = self.category
        context['parent_category'] = self.category.get_ancestors()
        context['flag'] = self.flag

        return context
