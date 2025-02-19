
from django.urls import path
from tabloide.views import PostListView, CreatedByListView, CategoryPostView, TagListView, SearchListView, PostView

app_name = 'tabloide'

urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('created_by/<int:author_pk>/', CreatedByListView.as_view(), name='created_by'),
    path('post/<slug:slug>/', PostView.as_view(), name='post'),
    path('tag/<slug:slug>/', TagListView.as_view(), name='tag'),
    path('category/<slug:slug>/', CategoryPostView.as_view(), name='category'),
    path('search/', SearchListView.as_view(), name='search'),
]