from django.shortcuts import redirect
from django.urls import path
from . import views

app_name='trade'

urlpatterns = [
    path('', lambda req: redirect('trade:item_list')),
    path('item/new/', views.item_new, name='item_new'),
    path('item/list/', views.item_list, name='item_list'),

    path('item/detail/<int:pk>/', views.item_detail, name='item_detail'),
    path('item/update/<int:pk>/', views.item_update, name='item_update'),
    path('item/delete/<int:pk>/', views.item_delete, name='item_delete'),

    path('comment/update/<int:pk>/<int:cid>/', views.comment_update, name='comment_update'),
    path('comment/delete/<int:pk>/<int:cid>/', views.comment_delete, name='comment_delete'),

    path('order/new/<int:item_id>/', views.order_new, name='order_new'),
    path('order/<int:item_id>/pay/<merchant_uid>/', views.order_pay, name='order_pay'),
    path('order/cancle/<int:order_id>/', views.order_cancle, name='order_cancle'),

    path('histroy/', views.trade_history, name='trade_history'),
]