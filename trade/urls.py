from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'trade'

urlpatterns = [
    path('', lambda req: redirect('mypage:root')),

    path('item/new/', views.ItemNew.as_view(), name='item_new'),
    path('item/detail/<int:pk>/', views.ItemDetail.as_view(), name='item_detail'),
    path('item/update/<int:pk>/', views.ItemUpdate.as_view(), name='item_update'),
    path('item/delete/<int:pk>/', views.ItemDelete.as_view(), name='item_delete'),

    path('comment/update/<int:pk>/<int:cid>/', views.CommentUpdate.as_view(), name='comment_update'),
    path('comment/delete/<int:pk>/<int:cid>/', views.CommentDelete.as_view(), name='comment_delete'),

    path('order/new/<int:item_id>/', views.OrderNew.as_view(), name='order_new'),
    path('order/<int:item_id>/pay/<merchant_uid>/', views.OrderPay.as_view(), name='order_pay'),
    path('order/cancle/<int:order_id>/', views.OrderCancle.as_view(), name='order_cancle'),
    path('order/confirm/<int:order_id>/', views.OrderConfirm.as_view(), name='order_confirm'),
    path('seller/confirm/<int:order_id>/', views.SellerConfirm.as_view(), name='seller_confirm'),

    path('order/histroy/', views.OrderHistory.as_view(), name='order_history'),
    path('seller/histroy/', views.SellerHistory.as_view(), name='seller_history'),
    path('info/<int:oid>/', views.TradeInfo.as_view(), name='trade_info'),
    path('test/', views.test, name='test'),
]
