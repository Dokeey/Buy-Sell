from django.urls import path
from . import views

app_name = 'category'

urlpatterns = [
    path('<int:pk>/', views.categories, name='categories'),
]