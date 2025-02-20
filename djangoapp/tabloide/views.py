from tabloide.models import Product
from django.shortcuts import redirect
from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView, DetailView
from utils.soma import somar
from utils.scraper import scrape_product

PER_PAGE = 9

class ProductListView(ListView):
    template_name = 'tabloide/pages/index.html'
    paginate_by = PER_PAGE
    queryset = Product.objects.get_published()
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'Home | ',
                'valor_soma': somar(900.0, 1200.0),
            }
        )
        return context

class TagListView(ProductListView):
    allow_empty = False
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(tags__slug=self.kwargs.get('slug'))
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title = f'{self.object_list[0].tags.first().name} | '
        context.update(
            {
                'page_title': page_title,
            }
        )        
        return context
    
class SearchListView(ProductListView):
    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self._search_value = ''
        
    def setup(self, request, *args, **kwargs):
        self._search_value = request.GET.get('search','').strip() 
        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(
            Q(title__icontains=self._search_value) |
            Q(excerpt__icontains=self._search_value) |
            Q(content__icontains=self._search_value)
        )[0:PER_PAGE]
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title = f'{self._search_value[:30]} - Search | '
        context.update(
            {
                'page_title': page_title,
                'search_value': self._search_value,
            }
        )        
        return context

    def get(self, request, *args, **kwargs):
        if self._search_value == '':
            return redirect('tabloide:index')
        return super().get(request, *args, **kwargs)

class ProductView(DetailView):
    model = Product
    template_name = 'tabloide/pages/post.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.get_object()
        page_title = f'{post.title} | '
        ctx.update(
            {
                'page_title': page_title,
                'product_values': scrape_product(post.vitrine_link),
            }
        )
        return ctx
    
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
    
