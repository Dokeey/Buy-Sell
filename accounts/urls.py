from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.SigninView.as_view(), name='login'),
    path('logout/', views.signout, name='logout'),
]