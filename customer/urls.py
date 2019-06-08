from django.urls import path
from . import views
app_name = 'customer'

urlpatterns = [

    path('faq/', views.customer_faq, name='customer_faq'),
    path('ask/', views.customer_ask, name='customer_ask'),
    path('ask/new/', views.customer_ask_new, name='customer_ask_new'),
    path('ask/edit/<int:ask_id>/', views.customer_ask_edit, name='customer_ask_edit'),
    path('ask/detail/<int:ask_id>/', views.customer_ask_detail, name='customer_ask_detail'),
]