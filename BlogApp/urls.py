from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('home/', views.home_view, name='article_home'),
    path('list/', views.listArticles, name='article_list'),
    path('listLV/', ArticleListView.as_view(), name='article_list_view'),
    path('details/<int:pk>/', ArticleDetailView.as_view(), name='article_details_view'),
    path('add/', ArticleCreateView.as_view(), name='article_create_view'),
    path('update/<int:pk>/', ArticleUpdateView.as_view(), name='article_update_view'),
    path('delete/<int:pk>/', ArticleDeleteView.as_view(), name='article_delete_view'),
    path('article/<int:pk>/like/', views.like_article, name='article_like'),
    path('article/<int:pk>/dislike/', views.dislike_article, name='article_dislike'),
]
