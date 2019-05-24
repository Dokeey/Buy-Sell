from django.urls import path
from . import views

urlpatterns = [
    path('sginup/', views.sginup, name='sginup')
]