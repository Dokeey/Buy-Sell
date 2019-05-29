from django.urls import path
from . import views

app_name='trade'

urlpatterns = [
    path('newitem/', views.item_new, name='item_new')
]