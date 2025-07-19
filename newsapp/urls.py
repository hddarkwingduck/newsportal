from django.urls import path
from .views import (
    home, article_list, signup, profile, ArticleListView,
    JournalistListView, PublisherListView, approve_article,
    editor_dashboard, journalist_dashboard, subscriptions,
    submit_article,
)

urlpatterns = [
    path('', home, name='home'),
    path('articles/', article_list, name='article_list_html'),
    path('signup/', signup, name='signup'),
    path('accounts/profile/', profile, name='profile'),
    path('api/articles/', ArticleListView.as_view(),
         name='article_list'),
    path('api/journalists/', JournalistListView.as_view(),
         name='journalist_list'),
    path('api/publishers/', PublisherListView.as_view(), name='publisher_list'),
    path('approve_article/<int:article_id>/', approve_article, name='approve_article'),
    path('editor_dashboard/', editor_dashboard, name='editor_dashboard'),
    path('journalist_dashboard/', journalist_dashboard, name='journalist_dashboard'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('articles/submit/', submit_article, name='submit_article'),
]
