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
    path('test/', views.test),
]