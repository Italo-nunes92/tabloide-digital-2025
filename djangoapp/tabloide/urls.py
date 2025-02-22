
from django.urls import path
from tabloide.views import ProductListView, TagListView, SearchListView, ProductView, CategoryPostView, SelecionarCidadeView

app_name = 'tabloide'

urlpatterns = [
    path('', SelecionarCidadeView.as_view(), name='index'),
    path('product/<slug:slug>/', ProductView.as_view(), name='product'),
    path('tag/<slug:slug>/', TagListView.as_view(), name='tag'),
    path('search/', SearchListView.as_view(), name='search'),
    path('category/<slug:slug>/', CategoryPostView.as_view(), name='category'),
    path('tabloide/', ProductListView.as_view() , name='tabloide'),

]