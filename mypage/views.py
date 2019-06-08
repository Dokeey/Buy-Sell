from django.shortcuts import render, redirect
from .models import WishList
# Create your views here.

def mypage_main(request):
    return render(request, 'mypage/main.html')


def wishlist(request):
    wishlist_set = request.user.wishlist_set.all()
    return render(request, 'mypage/wishlist.html', {
        'wishlist_set':wishlist_set
    })

def wishlist_new(request, item_id):
    if not request.user.wishlist_set.filter(item_id=item_id):
        WishList.objects.create(user=request.user, item_id=item_id)
    return redirect('mypage:wishlist')

def wishlist_delete(request, item_id):
    request.user.wishlist_set.filter(item_id=item_id).delete()
    return redirect('mypage:wishlist')
