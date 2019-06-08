from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', lambda req: redirect('mypage:main')),
    path('main/', views.mypage_main, name='main'),
]