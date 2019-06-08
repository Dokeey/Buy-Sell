from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', lambda req: redirect('accounts:profile')),
    path('signup/', views.signup, name='signup'),
    path('login/', views.SigninView.as_view(), name='login'),
    path('logout/', views.signout, name='logout'),
    path('withdrawal/', views.withdrawal, name='withdrawal'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/edit/pw/', views.pw_edit, name='pw_edit'),

    path('accounts/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('password_reset/', views.MyPasswordResetView.as_view(), name='password_reset'),
	path('reset/<uidb64>/<token>' ,views.MyPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('id_find/', views.IdFindView.as_view(), name='id_find'),

]