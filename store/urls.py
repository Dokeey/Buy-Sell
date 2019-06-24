from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [

    ##path('profile/', views.my_store_profile, name='my_store_profile'),
    #path('profile/', MyStoreProfileView.as_view(), name='my_store_profile'),
    #path('profile/edit/', views.store_profile_edit, name='store_profile_edit'),
    path('profile/edit/', views.StoreProfileEditView.as_view(), name='store_profile_edit'),
    path('question/<int:pk>/', views.store_question, name='store_question'),
    path('question/<int:pk>/edit/<int:cid>/', views.StoreQuestionEditView.as_view(), name='store_question_edit'),
    path('question/<int:pk>/delete/<int:cid>/', views.store_question_del, name='store_question_del'),

    path('grade/<int:pk>/', views.store_grade, name='store_grade'),
    path('grade/<int:pk>/new/<int:item_id>',views.store_grade_new, name='store_grade_new'),
    path('grade/<int:pk>/edit/<int:gid>/', views.store_grade_edit, name='store_grade_edit'),
    path('grade/<int:pk>/del/<int:gid>/',views.store_grade_del, name='store_grade_del'),
    # path('grade/<int:pk>/del/<int:gid>/', StoreGradeDelView.as_view(), name='store_grade_del'),
    #
    #path('sell/list/<int:pk>/', views.store_sell_list, name='store_sell_list'),
    path('sell/list/<int:pk>/', views.store_sell_list, name='store_sell_list'),
    # path('sell/list/<int:pk>/', views.StoreSellListView.as_view(), name='store_sell_list'),
]