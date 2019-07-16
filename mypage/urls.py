from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', lambda req: redirect('mypage:wishlist'), name='root'),
    path('wishlist/', views.WishListLV.as_view(), name='wishlist'),
    path('wishlist/<int:item_id>/', views.WishListTV.as_view(), name='wishlist_action'),

    path('follow/', views.FollowLV.as_view(), name='follow'),
    path('follow/<int:store_id>/', views.FollowTV.as_view(), name='follow_action'),
]