from django.urls import path

from . import views

app_name = 'store'

urlpatterns = [

    path('profile/edit/', views.StoreProfileEditView.as_view(), name='store_profile_edit'),
    path('question/<int:pk>/', views.StoreQuestionLCView.as_view(), name='store_question'),
    path('question/<int:pk>/edit/<int:cid>/', views.StoreQuestionEditView.as_view(), name='store_question_edit'),
    path('question/<int:pk>/delete/<int:cid>/', views.StoreQuestionDelView.as_view(), name='store_question_del'),

    path('grade/<int:pk>/', views.StoreGradeListView.as_view(), name='store_grade'),
    path('grade/<int:pk>/new/<int:item_id>',views.StoreGradeCreateView.as_view(), name='store_grade_new'),
    path('grade/<int:pk>/edit/<int:gid>/', views.StoreGradeEditView.as_view(), name='store_grade_edit'),
    path('grade/<int:pk>/del/<int:gid>/', views.StoreGradeDelView.as_view(), name='store_grade_del'),

    path('sell/list/<int:pk>/', views.StoreSellListView.as_view(), name='store_sell_list'),

    path('star/store/hit/', views.StarStoreHitListView.as_view(), name='star_store_hit'),
    path('star/store/grade/', views.StarStoreGradeListView.as_view(), name='star_store_grade'),
    path('star/store/sell/', views.StarStoreSellListView.as_view(), name='star_store_sell'),
    path('star/store/follow/', views.StarStoreFollowListView.as_view(), name='star_store_follow'),
    #path('profile/', views.my_store_profile, name='my_store_profile'),
]