from django.urls import path
from .views import (
    home, article_list, signup, profile, ArticleListView,
    JournalistListView, PublisherListView, approve_article,
    editor_dashboard, journalist_dashboard, subscriptions,
    submit_article, add_publisher, browse_publishers, browse_journalists,
    subscribe_publisher, unsubscribe_publisher, subscribe_journalist,
    unsubscribe_journalist,
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
    path('publishers/add/', add_publisher, name='add_publisher'),
    path('browse_publishers/', browse_publishers, name='browse_publishers'),
    path('browse_journalists/', browse_journalists, name='browse_journalists'),
    path('subscribe_publisher/<int:pk>/', subscribe_publisher, name='subscribe_publisher'),
    path('unsubscribe_publisher/<int:pk>/', unsubscribe_publisher, name='unsubscribe_publisher'),
    path('subscribe_journalist/<int:pk>/', subscribe_journalist, name='subscribe_journalist'),
    path('unsubscribe_journalist/<int:pk>/', unsubscribe_journalist, name='unsubscribe_journalist'),
]
