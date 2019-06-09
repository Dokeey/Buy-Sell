from django.urls import path

from . import views

app_name = 'policy'

urlpatterns = [
    path('service/', views.policy_service, name='policy_service'),
    path('privacy/', views.policy_privacy, name='policy_privacy'),
    path('location/', views.policy_location, name='policy_location')

]