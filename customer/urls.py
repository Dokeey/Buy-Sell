from django.urls import path
from . import views
app_name = 'customer'

urlpatterns = [
    path('faq/', views.CustomerFAQView.as_view(), name='customer_faq'),
    path('faq/search/', views.CustomerFAQSearch.as_view(), name='customer_faq_search'),
    path('ask/', views.CustomerAskListView.as_view(), name='customer_ask'),
    path('ask/new/', views.CustomerAskCreateView.as_view(), name='customer_ask_new'),
    path('ask/edit/<int:ask_id>/', views.CustomerAskEditView.as_view(), name='customer_ask_edit'),
    path('ask/detail/<int:ask_id>/', views.CustomerAskDetailView.as_view(), name='customer_ask_detail'),
    path('notice/',views.CustomerNoticeList.as_view(), name='customer_notice'),
]