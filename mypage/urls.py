from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', lambda req: redirect('mypage:main'), name='root'),
    path('main/', views.mypage_main, name='main'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/<int:item_id>/', views.wishlist_new, name='wishlist_new'),
    path('wishlist/delete/<int:item_id>/', views.wishlist_delete, name='wishlist_delete'),
]