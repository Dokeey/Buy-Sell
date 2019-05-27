from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.SigninView.as_view(), name='login'),
    path('logout/', views.signout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/edit/pw', views.pw_edit, name='pw_edit'),
    path('accounts/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('', lambda req: redirect('accounts:profile')),
]