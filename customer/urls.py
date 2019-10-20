from django.urls import path
from . import views
app_name = 'customer'

urlpatterns = [

    # path('', views.customer, name='customer'),
    path('faq/', views.CustomerFAQView.as_view(), name='customer_faq'),
    path('ask/', views.CustomerAskListView.as_view(), name='customer_ask'),
    path('ask/new/', views.CustomerAskCreateView.as_view(), name='customer_ask_new'),
    path('ask/edit/<int:ask_id>/', views.CustomerAskEditView.as_view(), name='customer_ask_edit'),
    path('ask/detail/<int:ask_id>/', views.CustomerAskDetailView.as_view(), name='customer_ask_detail'),
    path('notice/',views.CustomerNoticeList.as_view(), name='customer_notice'),
    # path('notice/<int:pk>', views.CustomerNoticeDetail.as_view(), name='notice_detail'),
]