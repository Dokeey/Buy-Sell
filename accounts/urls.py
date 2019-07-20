from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', lambda req: redirect('accounts:profile')),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.SigninView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user_delete/', views.UserDeleteView.as_view(), name='user_delete'),

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/edit/pw/', views.PasswordChange.as_view(), name='pw_edit'),

    path('accounts/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('password_reset/', views.MyPasswordResetView.as_view(), name='password_reset'),
	path('reset/<uidb64>/<token>' ,views.MyPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('id_find/', views.IdFindView.as_view(), name='id_find'),

]