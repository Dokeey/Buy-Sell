from django.urls import path
from . import views

app_name = 'category'

urlpatterns = [
    path('<int:pk>/', views.CategoryItemList.as_view(), name='category_item'),
    path('search/', views.SearchItemList.as_view(), name='search_item'),
]