from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, RedirectView, TemplateView
from django.views.generic.list import MultipleObjectMixin
from hitcount.models import HitCount

from accounts.models import Profile
from mypage.models import WishList, Follow

from accounts.supporter import send_mail
from .models import Item, ItemImage, ItemComment, Order
from .forms import ItemForm, ItemUpdateForm, ItemCommentForm, PayForm, OrderForm


def test(request):
    return render(request, 'trade/test.html', {
        'items': Item.objects.all()
    })


@method_decorator(login_required, name='dispatch')
class ItemNew(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'trade/item_new.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()

        for field in self.request.FILES.keys():
            for image in self.request.FILES.getlist(field):
                img = ItemImage(item=self.object, photo=image)
                img.save()

        data = {'is_valid': True}
        return JsonResponse(data)

    def form_invalid(self, form):
        error = form.errors
        data = {'is_valid': False, 'error': error}
        return JsonResponse(data)


@method_decorator(login_required, name='post')
class ItemDetail(MultipleObjectMixin, CreateView):
    model = ItemComment
    template_name = 'trade/item_detail.html'
    form_class = ItemCommentForm
    paginate_by = 5
    context_object_name = 'comments'

    def get(self, request, *args, **kwargs):
        self.item = get_object_or_404(Item, pk=self.kwargs.get('pk'))
        self.queryset = self.model.objects.filter(item=self.item, parent=None)
        self.object_list = self.queryset
        return super().get(request, *args, **kwargs)

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

        self.pk = self.kwargs.get('pk')
        items = Item.objects.filter(id=self.pk)
        items = items.select_related('user__storeprofile')
        items = items.prefetch_related('itemcomment_set')
        items = items.prefetch_related('itemimage_set')
        context['item'] = items[0]
        if context['item'].itemimage_set.exists():
            context['item_images_first_photo_url'] = context['item'].itemimage_set.first().photo.url
        else:
            context['item_images_first_photo_url'] = None

        context['hit_count'] = HitCount.objects.get_for_object(context['item']).hits
        context['wish_ctn'] = WishList.objects.filter(item=context['item']).count()
        context['follow_ctn'] = Follow.objects.filter(store=context['item'].user.storeprofile).count()
        context['items'] = context['item'].user.item_set.filter(~Q(id=context['item'].id), pay_status='ready')
        context['items'] = context['items'].prefetch_related('itemimage_set')[:3]
        context['items_ctn'] = context['items'].count()
        context['kakao_key'] = settings.KAKAO_KEY_JS
        context['facebook_key'] = settings.FACEBOOK_KEY
        return context

    def form_valid(self, form):
        try:
            parent_id = int(self.request.POST.get('parent_id'))
        except:
            parent_id = None

        if parent_id:
            parent_obj = ItemComment.objects.get(id=parent_id)
            if parent_obj:
                form.instance.parent = parent_obj

        form.instance.user = self.request.user
        item = get_object_or_404(Item, pk=self.kwargs.get('pk'))
        form.instance.item = item
        self.object = form.save()

        # 물품 문의알림 메일 발송
        if item.itemcomment_set.all().count() % 5 == 1:
            send_mail(
                '[Buy & Sell] {}님 물품에 문의글이 생겼습니다.'.format(item.user.username),
                [item.user.email],
                html=render_to_string('trade/item_comment_alert.html', {
                    'user': item.user,
                    'domain': self.request.META['HTTP_HOST'],
                    'item': item,
                }),
            )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('trade:item_detail', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class ItemUpdate(UpdateView):
    model = Item
    form_class = ItemUpdateForm
    template_name = 'trade/item_update.html'

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=self.kwargs.get('pk'))
        if item.user != self.request.user:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('root')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        item = form.save(commit=False)
        if item.order_set.filter(status='reserv'):
            messages.error(self.request, '예약중인 상품은 변경할 수 없습니다.')
            return redirect('trade:item_detail', self.kwargs.get('pk'))

        self.object = form.save()

        data = {'id': item.id, 'pay_status': item.get_pay_status_display()}
        return JsonResponse(data)

    def get_success_url(self):
        return reverse_lazy('trade:item_detail', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class ItemDelete(DeleteView):
    model = Item
    template_name = 'trade/item_delete.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.user:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('root')
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        self.success_url = reverse_lazy('store:store_sell_list', kwargs={'pk': self.request.user.storeprofile.id})
        return super().get_success_url()


@method_decorator(login_required, name='dispatch')
class CommentUpdate(UpdateView):
    model = ItemComment
    form_class = ItemCommentForm
    pk_url_kwarg = 'cid'
    template_name = 'trade/comment_update.html'

    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(ItemComment, pk=self.kwargs.get(self.pk_url_kwarg))
        if self.request.user != comment.user:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('trade:item_detail', self.kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        comment = get_object_or_404(ItemComment, pk=self.kwargs.get(self.pk_url_kwarg))
        self.object = form.save()

        data = {'id': comment.id, 'msg': form.cleaned_data['message']}
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class CommentDelete(DeleteView):
    model = ItemComment
    template_name = 'trade/comment_delete.html'
    pk_url_kwarg = 'cid'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.user:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('trade:item_detail', self.kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        id = self.object.id
        item = self.object.item
        self.object.delete()

        cmt_ctn = item.itemcomment_set.all().count()
        data = {'id': id, 'cmt_ctn': cmt_ctn}
        return JsonResponse(data)


# 물품 구매하기
@method_decorator(login_required, name='dispatch')
class OrderNew(FormView):
    form_class = OrderForm
    template_name = 'trade/order_form.html'

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=self.kwargs.get('item_id'))

        if item.user == self.request.user:
            messages.error(self.request, '자신의 물품은 구매할수 없습니다.')
            return self.get_success_url()

        if item.pay_status != "ready":
            messages.error(self.request, '이미 예약이 되었거나 판매완료 상품입니다.')
            return self.get_success_url()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = get_object_or_404(Item, pk=self.kwargs.get('item_id'))
        return context

    def get_initial(self):
        self.initial = {'email': self.request.user.email}
        return super().get_initial()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': get_object_or_404(Profile, user=self.request.user),
        })
        return kwargs

    def form_valid(self, form):
        item = self.get_context_data()['item']

        order = Order.objects.create(user=self.request.user,
                                     item=item,
                                     amount=item.amount,
                                     email=form.cleaned_data['email'],
                                     username=form.cleaned_data['username'],
                                     phone=form.cleaned_data['phone'],
                                     post_code=form.cleaned_data['post_code'],
                                     address=form.cleaned_data['address'],
                                     detail_address=form.cleaned_data['detail_address'],
                                     requirement=form.cleaned_data['requirement'],
                                     pay_choice=form.cleaned_data['pay_choice'],
                                     )

        if form.cleaned_data['pay_choice'] == 'import':
            return redirect('trade:order_pay', self.kwargs.get('item_id'), str(order.merchant_uid))
        elif form.cleaned_data['pay_choice'] == 'bank_trans':
            order.status = 'reserv'
            order.is_active = False
            order.update()

            # 물품 주문알림 메일 발송
            send_mail(
                '[Buy & Sell] 구매자가 {}님의 물품을 예약하였습니다.'.format(item.user.username),
                [item.user.email],
                html=render_to_string('trade/item_sell_alert.html', {
                    'user': item.user,
                    'domain': self.request.META['HTTP_HOST'],
                    'item': item,
                }),
            )

            return redirect('trade:trade_info', order.id)

    def get_success_url(self):
        next_url = self.request.GET.get('next') or 'mypage:root'  # next get인자가 있으면 넣고 없으면 'profile' 넣기
        return redirect(next_url)


# Import 연동
@method_decorator(login_required, name='dispatch')
class OrderPay(CreateView):
    model = Order
    form_class = PayForm
    template_name = 'trade/pay_form.html'
    success_url = reverse_lazy('trade:order_history')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': get_object_or_404(Order, user=self.request.user, merchant_uid=self.kwargs.get('merchant_uid'),
                                          status='ready'),
        })
        return kwargs

    def form_valid(self, form):
        # 물품 주문알림 메일 발송
        self.object = form.save()
        send_mail(
            '[Buy & Sell] 구매자가 {}님의 물품을 결제하였습니다.'.format(self.object.item.user.username),
            [self.object.item.user.email],
            html=render_to_string('trade/item_sell_alert.html', {
                'user': self.object.item.user,
                'domain': self.request.META['HTTP_HOST'],
                'item': self.object.item,
            }),
        )
        return redirect(self.get_success_url())


# 구매취소
@method_decorator(login_required, name='dispatch')
class OrderCancle(RedirectView):
    url = 'trade:order_history'

    def get(self, request, *args, **kwargs):
        try:
            queryset = Order.objects.get(id=self.kwargs.get('order_id'))

            if not self.request.user in (queryset.user, queryset.item.user):
                messages.error(self.request, '잘못된 접근입니다.')
                return redirect(self.url)

            if queryset.status == "cancelled":
                messages.error(self.request, '이미 주문을 취소하셨습니다.')
                return redirect(self.url)
            elif queryset.status == "success":
                messages.error(self.request, '거래가 완료된 상태입니다.')
                return redirect(self.url)

            queryset.cancel()
            messages.info(self.request, '주문을 취소하셨습니다.')
        except:
            messages.error(self.request, '유효하지 않은 상품입니다.')

        return redirect(self.url)


# 구매확정
@method_decorator(login_required, name='dispatch')
class OrderConfirm(RedirectView):
    url = 'trade:order_history'

    def get(self, request, *args, **kwargs):
        try:
            queryset = Order.objects.get(id=self.kwargs.get('order_id'))

            if self.request.user != queryset.user or not queryset.is_active:
                messages.error(self.request, '잘못된 접근입니다.')
                return redirect(self.url)

            if queryset.status == "success":
                messages.error(self.request, '이미 구매확정 하셨습니다.')
                return redirect(self.url)
            elif queryset.status == "cancelled":
                messages.error(self.request, '거래가 취소된 상품입니다.')
                return redirect(self.url)

            elif queryset.status in ('reserv', 'paid'):
                queryset.status = 'success'
                queryset.update()

                messages.info(self.request, '구매를 축하드립니다!!')
        except:
            messages.error(self.request, '유효하지 않은 상품입니다.')

        return redirect(self.url)


# 입금확인
@method_decorator(login_required, name='dispatch')
class SellerConfirm(RedirectView):
    url = 'trade:seller_history'

    def get(self, request, *args, **kwargs):
        try:
            queryset = Order.objects.get(id=self.kwargs.get('order_id'))

            if self.request.user != queryset.item.user:
                messages.error(self.request, '잘못된 접근입니다.')
                return redirect(self.url)

            if queryset.status == "success":
                messages.error(self.request, '이미 구매확정 하셨습니다.')
                return redirect(self.url)
            elif queryset.status == "cancelled":
                messages.error(self.request, '거래가 취소된 상품입니다.')
                return redirect(self.url)

            if not queryset.is_active:
                queryset.is_active = True
                queryset.save()
                messages.info(self.request, '입금을 확인하셨습니다.')

        except:
            messages.error(self.request, '유효하지 않은 상품입니다.')

        return redirect(self.url)


# 거래내역
class BaseHistory(ListView):
    model = Order
    template_name = 'trade/order_history.html'
    ordering = '-created_at'
    paginate_by = 3

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


# 구매내역
@method_decorator(login_required, name='dispatch')
class OrderHistory(BaseHistory):
    context_object_name = 'order_list'

    def get_queryset(self):
        self.queryset = self.request.user.order_set.all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_ctn'] = self.queryset.count()
        return context


# 판매내역
@method_decorator(login_required, name='dispatch')
class SellerHistory(BaseHistory):
    template_name = 'trade/seller_history.html'
    context_object_name = 'sell_list'

    def get_queryset(self):
        orders = self.model.objects.all()
        sell_list = []
        for order in orders:
            if order.item.user == self.request.user:
                sell_list.append(order.id)

        self.queryset = self.model.objects.filter(id__in=sell_list)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sell_ctn'] = self.queryset.count()
        return context


# 거래에 필요한 구매자, 판매자 정보
@method_decorator(login_required, name='dispatch')
class TradeInfo(TemplateView):
    template_name = 'trade/trade_info.html'

    def get(self, request, *args, **kwargs):
        self.order = Order.objects.get(id=self.kwargs.get('oid'))
        if not self.request.user in (self.order.user, self.order.item.user):
            messages.error(self.request, '잘못된 접근입니다.')
            return redirect('root')

        if not self.order.status in ('paid', 'reserv', 'success'):
            messages.error(self.request, '잘못된 접근입니다.')
            return redirect('root')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context
