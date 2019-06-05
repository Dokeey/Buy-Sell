from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from category.models import SubCategory
from accounts.models import Profile

from .models import Item, ItemComment, Order
from .forms import ItemForm, ItemUpdateForm, ItemCommentForm, PayForm, OrderForm


@login_required
def item_new(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = get_object_or_404(SubCategory, id=form.cleaned_data['category_tmp'])
            item.user = request.user
            item.photo = form.cleaned_data['photo']
            form.save()
            return redirect('trade:item_list')
    else:
        form = ItemForm
    return render(request, 'trade/item_new.html', {
        'form': form
    })


def item_list(request):
    items = Item.objects.all()
    return render(request, 'trade/item_list.html', {
        'items': items
    })


@login_required
def my_item_list(request):
    items = Item.objects.filter(user=request.user)
    return render(request, 'trade/item_list.html', {
        'items': items
    })


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    comments = ItemComment.objects.filter(item=item, parent=None)
    form = ItemCommentForm
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        form = ItemCommentForm(request.POST)
        if form.is_valid():
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = ItemComment.objects.get(id=parent_id)
                if parent_obj:
                    replay_comment = form.save(commit=False)
                    replay_comment.parent = parent_obj
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.item = item
            new_comment.save()
        return redirect('trade:item_detail', pk)
    return render(request, 'trade/item_detail.html', {
        'item': item,
        'comments': comments,
        'form': form,
    })


def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemUpdateForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = get_object_or_404(SubCategory, id=form.cleaned_data['category_tmp'])
            item.user = request.user
            item.photo = form.cleaned_data['photo']
            form.save()
        return redirect('trade:item_detail', pk)
    else:
        form = ItemUpdateForm(instance=item)
    return render(request, 'trade/item_new.html',{
        'form': form
    })


def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    return redirect('trade:item_list')


def comment_update(request, pk, cid):
    comment = get_object_or_404(ItemComment, pk=cid)
    if request.method == "POST":
        form = ItemCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
        return redirect('trade:item_detail', pk)
    else:
        form = ItemCommentForm(instance=comment)
    return render(request, 'trade/comment_update.html',{
        'form':form
    })


def comment_delete(reuqest, pk, cid):
    comment = get_object_or_404(ItemComment, pk=cid)
    comment.delete()
    return redirect('trade:item_detail', pk)


def order_new(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if item.pay_status != 'ready':
        buyer = get_object_or_404(Profile, user=request.user)
        if request.method == "POST":
            form = OrderForm(request.POST, instance=buyer)
            if form.is_valid():
                if form.cleaned_data['pay_choice'] == 'import':
                    order = Order.objects.create(user=request.user, item=item, name=item.title, amount=item.amount,
                        buyer_email=form.cleaned_data['email'], buyer_name=form.cleaned_data['nick_name'],
                        buyer_tel=form.cleaned_data['phone'], buyer_postcode=form.cleaned_data['post_code'],
                        buyer_addr=form.cleaned_data['address'] + form.cleaned_data['detail_address'],
                    )
                    return redirect('trade:order_pay', item_id, str(order.merchant_uid))
                elif form.cleaned_data['pay_choice'] == 'bank_trans':
                    return render(request, 'trade/seller_info.html', {
                        'seller': item.user
                    })

            else:
                messages.error(request, '유효하지 않은 상품입니다.')
        else:
            form = OrderForm(instance=buyer)
    else:
        messages.error(request, '이미 예약이 되었거나 판매완료 상품입니다.')
    return render(request, 'trade/order_form.html',{
        'item':item,
        'form':form,
    })


def order_pay(request, item_id, merchant_uid):
    order = get_object_or_404(Order, user=request.user, merchant_uid=merchant_uid, status='ready')

    if request.method == 'POST':
        form = PayForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = PayForm(instance=order)
    return render(request, 'trade/pay_form.html', {
        'form': form,
    })


def order_cancle(request, order_id):
    '선택된 주문에 대해 결제취소요청을 합니다.'

    try:
        queryset = Order.objects.get(pk=order_id, status='paid')
        queryset.cancel()
        messages.info(request, '주문을 취소하셨습니다.')
    except:
        messages.error(request, '이미 취소하셨거나, 유효하지 않은 상품입니다.')

    return redirect('accounts:profile')


def test(request):
    return render(request, 'trade/test.html')