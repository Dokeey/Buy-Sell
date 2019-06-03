from django.shortcuts import redirect
from django.urls import path
from . import views

app_name='trade'

urlpatterns = [
    path('', lambda req: redirect('trade:item_list')),
    path('item_new/', views.item_new, name='item_new'),
    path('item_list/', views.item_list, name='item_list'),
    path('my_item_list/', views.my_item_list, name='my_item_list'),
    path('item_detail/<int:pk>/', views.item_detail, name='item_detail'),
    path('item_update/<int:pk>/', views.item_update, name='item_update'),
    path('item_delete/<int:pk>/', views.item_delete, name='item_delete'),
    path('comment_update/<int:pk>/<int:cid>/', views.comment_update, name='comment_update'),
    path('comment_delete/<int:pk>/<int:cid>/', views.comment_delete, name='comment_delete'),
    path('test/', views.test),
]