from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [

    path('profile/', views.store_profile, name='store_profile'),
    path('profile/edit/', views.store_profile_edit, name='store_profile_edit'),
]