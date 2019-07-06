from django.contrib import messages
from django.shortcuts import render, redirect
from .models import WishList, Follow
# Create your views here.

def mypage_main(request):
    return render(request, 'mypage/layout.html')


def wishlist(request):
    wishlist_set = request.user.wishlist_set.all()
    return render(request, 'mypage/wishlist.html', {
        'wishlist_set':wishlist_set
    })

def wishlist_new(request, item_id):
    if not request.user.wishlist_set.filter(item_id=item_id):
        if request.user.item_set.filter(id=item_id):
            messages.error(request, '본인 상품은 찜할 수 없어요 ^^')
        else:
            WishList.objects.create(user=request.user, item_id=item_id)
    return redirect('mypage:wishlist')

def wishlist_delete(request, item_id):
    request.user.wishlist_set.filter(item_id=item_id).delete()
    return redirect('mypage:wishlist')


def follow(request):
    follow_set = request.user.follow_set.all()
    return render(request, 'mypage/follow.html', {
        'follow_set':follow_set
    })

def follow_new(request, store_id):
    if not request.user.follow_set.filter(store_id=store_id):
        if request.user.storeprofile.id == store_id:
            messages.error(request, '본인은 팔로우할 수 없어요 ^^')
            return redirect('store:store_sell_list', pk=store_id)
        else:
            Follow.objects.create(user=request.user, store_id=store_id)
    return redirect('mypage:follow')

def follow_delete(request, store_id):
    request.user.follow_set.filter(store_id=store_id).delete()
    return redirect('mypage:wishlist')