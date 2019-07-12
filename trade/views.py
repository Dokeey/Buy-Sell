from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, RedirectView, \
    TemplateView
from django.views.generic.detail import SingleObjectMixin
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from category.models import Category
from accounts.models import Profile
from mypage.models import WishList, Follow
from .models import Item, ItemImage, ItemComment, Order
from .forms import ItemForm, ItemUpdateForm, ItemCommentForm, PayForm, OrderForm

from time import time

def test(request):
    return render(request, 'trade/test.html')
# @login_required
# def item_new(request):
#     if request.method == "POST":
#         form = ItemForm(request.POST, request.FILES)
#         if form.is_valid():
#             item = form.save(commit=False)
#             item.user = request.user
#             item.photo = form.cleaned_data['photo']
#             form.save()
#             return redirect('store:my_store_profile')
#     else:
#         form = ItemForm
#     return render(request, 'trade/item_new.html', {
#         'form': form
#     })

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
        data = {'is_valid': False, 'error':error}
        return JsonResponse(data)

    def get_success_url(self):
        self.success_url = reverse_lazy('store:store_sell_list', kwargs={'pk': self.request.user.storeprofile.id})
        return super().get_success_url()


# def item_detail(request, pk):
#     item = get_object_or_404(Item, pk=pk)
#     comments = ItemComment.objects.filter(item=item, parent=None)
#     hit_count = HitCount.objects.get_for_object(item)
#     hit_count_response = HitCountMixin.hit_count(request, hit_count)
#     form = ItemCommentForm
#     if request.method == "POST":
#         if not request.user.is_authenticated:
#             return redirect('accounts:login')
#         form = ItemCommentForm(request.POST)
#         if form.is_valid():
#             parent_obj = None
#             try:
#                 parent_id = int(request.POST.get('parent_id'))
#             except:
#                 parent_id = None
#             if parent_id:
#                 parent_obj = ItemComment.objects.get(id=parent_id)
#                 if parent_obj:
#                     replay_comment = form.save(commit=False)
#                     replay_comment.parent = parent_obj
#             new_comment = form.save(commit=False)
#             new_comment.user = request.user
#             new_comment.item = item
#             new_comment.save()
#         return redirect('trade:item_detail', pk)
#     return render(request, 'trade/item_detail.html', {
#         'item': item,
#         'comments': comments,
#         'form': form,
#     })

class ItemDetail(CreateView):
    model = ItemComment
    template_name = 'trade/item_detail.html'
    form_class = ItemCommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.pk = self.kwargs.get('pk')
        context['item'] = get_object_or_404(Item, pk=self.pk)
        context['comments'] = self.model.objects.filter(item=context['item'], parent=None)

        hit_count = HitCount.objects.get_for_object(context['item'])
        context['hit_count_response'] = HitCountMixin.hit_count(self.request, hit_count)

        context['wish_ctn'] = WishList.objects.filter(item=context['item']).count()
        context['follow_ctn'] = Follow.objects.filter(store=context['item'].user.storeprofile).count()

        items = context['item'].user.item_set.filter(pay_status='ready')
        item_list = []
        for item in items:
            if item == context['item']: continue
            if len(item_list) == 3: break
            item_list.append(item)

        context['items'] = item_list
        context['items_ctn'] = items.count()
        return context

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        try:
            parent_id = int(self.request.POST.get('parent_id'))
        except:
            parent_id = None

        if parent_id:
            parent_obj = ItemComment.objects.get(id=parent_id)
            if parent_obj:
                form.instance.parent = parent_obj

        form.instance.user = self.request.user
        form.instance.item = self.get_context_data()['item']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('trade:item_detail', kwargs={'pk': self.pk})


# def item_update(request, pk):
#     item = get_object_or_404(Item, pk=pk)
#     if request.method == "POST":
#         form = ItemUpdateForm(request.POST, request.FILES, instance=item)
#         if form.is_valid():
#             item = form.save(commit=False)
#             if item.order_set.filter(status='reserv'):
#                 messages.error(request, '예약중인 상품은 변경할 수 없습니다.')
#             else:
#                 # item.category = get_object_or_404(Category, id=form.cleaned_data['category_tmp'])
#                 item.user = request.user
#                 item.photo = form.cleaned_data['photo']
#                 form.save()
#         return redirect('trade:item_detail', pk)
#     else:
#         form = ItemUpdateForm(instance=item)
#     return render(request, 'trade/item_new.html',{
#         'form': form
#     })

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

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('trade:item_detail', kwargs={'pk': self.kwargs.get('pk')})


# def item_delete(request, pk):
#     item = get_object_or_404(Item, pk=pk)
#     item.delete()
#     return redirect('trade:item_list')

@method_decorator(login_required, name='dispatch')
class ItemDelete(DeleteView):
    model = Item
    template_name = 'trade/item_delete.html'
    success_url = reverse_lazy('mypage:main')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.user:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('root')
        return super().get(request, *args, **kwargs)


# def comment_update(request, pk, cid):
#     comment = get_object_or_404(ItemComment, pk=cid)
#     if request.method == "POST":
#         form = ItemCommentForm(request.POST, instance=comment)
#         if form.is_valid():
#             form.save()
#         return redirect('trade:item_detail', pk)
#     else:
#         form = ItemCommentForm(instance=comment)
#     return render(request, 'trade/comment_update.html',{
#         'form':form
#     })

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

        data = {'id':comment.id, 'msg':form.cleaned_data['message']}
        return JsonResponse(data)

# def comment_delete(reuqest, pk, cid):
#     comment = get_object_or_404(ItemComment, pk=cid)
#     comment.delete()
#     return redirect('trade:item_detail', pk)

@method_decorator(login_required, name='dispatch')
class CommentDelete(DeleteView):
    model = ItemComment
    template_name = 'trade/item_delete.html'
    pk_url_kwarg = 'cid'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.user:
            messages.error(self.request, '잘못된 접근 입니다.')
            return redirect('trade:item_detail', self.kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = {'id':self.object.id}

        self.object.delete()
        return JsonResponse(data)

# def order_new(request, item_id):
#     item = get_object_or_404(Item, pk=item_id)
#     form = None
#     if item.pay_status == 'ready':
#         buyer = get_object_or_404(Profile, user=request.user)
#         if request.method == "POST":
#             form = OrderForm(request.POST, instance=buyer)
#             if form.is_valid():
#                 order = Order.objects.create(user=request.user, item=item, name=item.title, amount=item.amount,
#                     buyer_email=form.cleaned_data['email'],
#                     buyer_name=form.cleaned_data['nick_name'],
#                     buyer_tel=form.cleaned_data['phone'],
#                     buyer_postcode=form.cleaned_data['post_code'],
#                     buyer_addr=form.cleaned_data['address'] + form.cleaned_data['detail_address'],
#                 )
#                 if form.cleaned_data['pay_choice'] == 'import':
#                     return redirect('trade:order_pay', item_id, str(order.merchant_uid))
#                 elif form.cleaned_data['pay_choice'] == 'bank_trans':
#                     Order.objects.filter(user=request.user,
#                                          merchant_uid=order.merchant_uid,
#                                          status='ready'
#                                          ).update(status='reserv')
#                     reserv_order = Order.objects.get(user=request.user, merchant_uid=order.merchant_uid, status='reserv')
#                     reserv_order.update()
#
#                     return render(request, 'trade/seller_info.html', {
#                         'seller': item.user
#                     })
#
#             else:
#                 messages.error(request, '유효하지 않은 상품입니다.')
#         else:
#             form = OrderForm(instance=buyer)
#     else:
#         messages.error(request, '이미 예약이 되었거나 판매완료 상품입니다.')
#     return render(request, 'trade/order_form.html',{
#         'item':item,
#         'form':form,
#     })


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
                                     name=item.title,
                                     amount=item.amount,
                                     email=form.cleaned_data['email'],
                                     username=form.cleaned_data['username'],
                                     phone=form.cleaned_data['phone'],
                                     post_code=form.cleaned_data['post_code'],
                                     address=form.cleaned_data['address'],
                                     detail_address = form.cleaned_data['detail_address'],
                                     requirement = form.cleaned_data['requirement'],
                                     )

        if form.cleaned_data['pay_choice'] == 'import':
            return redirect('trade:order_pay', self.kwargs.get('item_id'), str(order.merchant_uid))
        elif form.cleaned_data['pay_choice'] == 'bank_trans':
            Order.objects.filter(user=self.request.user,
                                 merchant_uid=order.merchant_uid,
                                 status='ready'
                                 ).update(status='reserv', is_active=False)
            reserv_order = Order.objects.get(user=self.request.user, merchant_uid=order.merchant_uid, status='reserv')
            reserv_order.update()

            return render(self.request, 'trade/seller_info.html', {
                'seller': item.user
            })


    def get_success_url(self):
        next_url = self.request.GET.get('next') or 'mypage:main'  # next get인자가 있으면 넣고 없으면 'profile' 넣기
        return redirect(next_url)



# def order_pay(request, item_id, merchant_uid):
#     order = get_object_or_404(Order, user=request.user, merchant_uid=merchant_uid, status='ready')
#
#     if request.method == 'POST':
#         form = PayForm(request.POST, instance=order)
#         if form.is_valid():
#             form.save()
#             return redirect('accounts:profile')
#     else:
#         form = PayForm(instance=order)
#     return render(request, 'trade/pay_form.html', {
#         'form': form,
#     })


@method_decorator(login_required, name='dispatch')
class OrderPay(CreateView):
    model = Order
    form_class = PayForm
    template_name = 'trade/pay_form.html'
    success_url = reverse_lazy('trade:order_history')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': get_object_or_404(Order, user=self.request.user, merchant_uid=self.kwargs.get('merchant_uid'), status='ready'),
        })
        return kwargs



# def order_cancle(request, order_id):
#     '선택된 주문에 대해 결제취소요청을 합니다.'
#
#     try:
#         queryset = Order.objects.get(id=order_id)
#         queryset.cancel()
#         messages.info(request, '주문을 취소하셨습니다.')
#     except:
#         messages.error(request, '유효하지 않은 상품입니다.')
#
#     return redirect('trade:trade_history')


@method_decorator(login_required, name='dispatch')
class OrderCancle(RedirectView):
    url = 'trade:order_history'


    def get(self, request, *args, **kwargs):
        try:
            queryset = Order.objects.get(id=self.kwargs.get('order_id'))

            if not self.request.user in (queryset.user, queryset.item.user):
                messages.error(request, '잘못된 접근입니다.')
                return redirect(self.url)

            if queryset.status == "cancelled":
                messages.error(request, '이미 주문을 취소하셨습니다.')
                return redirect(self.url)
            elif queryset.status == "success":
                messages.error(request, '거래가 완료된 상태입니다.')
                return redirect(self.url)

            queryset.cancel()
            messages.info(request, '주문을 취소하셨습니다.')
        except:
            messages.error(request, '유효하지 않은 상품입니다.')

        return redirect(self.url)


@method_decorator(login_required, name='dispatch')
class OrderConfirm(RedirectView):
    url = 'trade:order_history'


    def get(self, request, *args, **kwargs):
        try:
            queryset = Order.objects.get(id=self.kwargs.get('order_id'))

            if self.request.user != queryset.user or not queryset.is_active:
                messages.error(request, '잘못된 접근입니다.')
                return redirect(self.url)

            if queryset.status == "success":
                messages.error(request, '이미 구매확정 하셨습니다.')
                return redirect(self.url)
            elif queryset.status == "cancelled":
                messages.error(request, '거래가 취소된 상품입니다.')
                return redirect(self.url)

            elif queryset.status in ('reserv','paid'):
                queryset.status = 'success'
                queryset.meta['paid_at'] = int(time())
                queryset.item.pay_status = 'sale_complete'
                queryset.item.save()
                queryset.save()

                messages.info(request, '구매를 축하드립니다!!')
        except:
            messages.error(request, '유효하지 않은 상품입니다.')

        return redirect(self.url)


@method_decorator(login_required, name='dispatch')
class SellerConfirm(RedirectView):
    url = 'trade:seller_history'

    def get(self, request, *args, **kwargs):
        try:
            queryset = Order.objects.get(id=self.kwargs.get('order_id'))

            if self.request.user != queryset.item.user:
                messages.error(request, '잘못된 접근입니다.')
                return redirect(self.url)

            if queryset.status == "success":
                messages.error(request, '이미 구매확정 하셨습니다.')
                return redirect(self.url)
            elif queryset.status == "cancelled":
                messages.error(request, '거래가 취소된 상품입니다.')
                return redirect(self.url)

            if not queryset.is_active:
                queryset.is_active = True
                queryset.save()
                messages.info(request, '입금을 확인하셨습니다.')

        except:
            messages.error(request, '유효하지 않은 상품입니다.')

        return redirect(self.url)
# @login_required
# def trade_history(request):
#     order_list = request.user.order_set.all()
#     orders = Order.objects.all()
#     sell_list = []
#     for order in orders:
#         if order.item.user == request.user:
#             sell_list.append(order)
#     return render(request, 'trade/trade_history.html',{
#         'order_list': order_list,
#         'sell_list': sell_list,
#     })


class BaseHistory(ListView):
    model = Order
    template_name = 'trade/order_history.html'
    ordering = '-created_at'
    paginate_by = 4

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

        return context


@method_decorator(login_required, name='dispatch')
class OrderHistory(BaseHistory):
    context_object_name = 'order_list'

    def get_queryset(self):
        self.queryset = self.request.user.order_set.all()
        return super().get_queryset()


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
