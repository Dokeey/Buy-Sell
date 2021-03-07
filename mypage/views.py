from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView

from .models import WishList, Follow


@method_decorator(login_required, name='dispatch')
class WishListLV(ListView):
    model = WishList
    context_object_name = 'wishlist_set'
    template_name = 'mypage/wishlist.html'
    paginate_by = 12

    def get_queryset(self):
        self.queryset = self.request.user.wishlist_set.all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
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
        return context


@method_decorator(login_required, name='dispatch')
class WishListTV(TemplateView):
    template_name = 'mypage/wishlist.html'

    def get(self, request, *args, **kwargs):
        if not request.user.wishlist_set.filter(item_id=self.kwargs.get('item_id')):
            if request.user.item_set.filter(id=self.kwargs.get('item_id')):
                messages.error(request, '본인 물품은 찜할 수 없어요 ^^')
            else:
                messages.info(request, '찜 하셨습니다')
                WishList.objects.create(user=request.user, item_id=self.kwargs.get('item_id'))
        else:
            messages.warning(request, '찜을 삭제 하셨습니다')
            request.user.wishlist_set.filter(item_id=self.kwargs.get('item_id')).delete()

        url = request.GET.get('next') or 'mypage:wishlist'
        return redirect(url)


@method_decorator(login_required, name='dispatch')
class FollowLV(ListView):
    model = Follow
    context_object_name = 'follow_set'
    template_name = 'mypage/follow.html'
    paginate_by = 6

    def get_queryset(self):
        self.queryset = self.request.user.follow_set.all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
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
        return context


@method_decorator(login_required, name='dispatch')
class FollowTV(TemplateView):
    template_name = 'mypage/follow.html'

    def get(self, request, *args, **kwargs):
        if not request.user.follow_set.filter(store_id=self.kwargs.get('store_id')):
            if request.user.storeprofile.id == self.kwargs.get('store_id'):
                messages.error(request, '본인은 팔로우할 수 없어요 ^^')
            else:
                messages.info(request, '팔로우 하셨습니다')
                Follow.objects.create(user=request.user, store_id=self.kwargs.get('store_id'))
        else:
            messages.warning(request, '팔로우를 삭제 하셨습니다')
            request.user.follow_set.filter(store_id=self.kwargs.get('store_id')).delete()

        url = request.GET.get('next') or 'mypage:follow'
        return redirect(url)
