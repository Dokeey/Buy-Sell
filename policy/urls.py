from django.urls import path

from . import views

app_name = 'policy'

urlpatterns = [
    path('service/', views.PolicyServiceView.as_view(), name='policy_service'),
    path('privacy/', views.PolicyPrivacyView.as_view(), name='policy_privacy'),
    # path('location/', views.policy_location, name='policy_location')

]