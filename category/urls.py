from django.urls import path
from . import views

app_name = 'category'

urlpatterns = [
    #path('', views.print_category, name='print_category'),
    path('<int:pk>/', views.categories, name='categories'),
    path('<int:cate_pk>/<int:pk>/',views.subcategories, name='subcategories'),
    path('test', views.test, name='test')
]