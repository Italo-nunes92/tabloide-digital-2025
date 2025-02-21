from tabloide.models import Product, Store
from tabloide.form import StoreForm
from django.shortcuts import redirect, render
from django.db.models import Q
from django.http import Http404
from django.views.generic import ListView, DetailView
from utils.scraper import scrape_product
from datetime import datetime, date

PER_PAGE = 9

class ProductListView(ListView):
    template_name = 'tabloide/pages/index.html'
    paginate_by = PER_PAGE
    queryset = Product.objects.get_published()

    
 

     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loja = self.request.GET.get('store')
        loja_escolhida = Store.objects.filter(title=loja).first()
        context.update(
            {
                'page_title': 'Home | ',
                'date': datetime.now().date(),
                'loja': loja_escolhida
            }
        )
        print(type(loja_escolhida))
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
            Q(excerpt__icontains=self._search_value)
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
    
class CategoryPostView(ProductListView):
    allow_empty = False
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(category__slug=self.kwargs.get('slug'))
                
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title = f'{self.object_list[0].category.name} | '
        context.update(
            {
                'page_title': page_title,
            }
        )        
        return context

class ProductView(DetailView):
    model = Product
    template_name = 'tabloide/pages/product.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.get_object()
        page_title = f'{product.title} | '
        ctx.update(
            {
                'page_title': page_title,
                'product_values': scrape_product(product.vitrine_link),
            }
        )
        return ctx
    
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
    
# class StoreSelectionView(View):
#     template_name = 'tabloide/pages/index.html'
#     form_class = StoreForm
    
#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         print("Esse aqui")
        
#         return render(request, self.template_name, {'form': form})
    
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             store = form.cleaned_data['title']
#             return redirect('tabloide:city_results', store=store.number)
#         return render(request, self.template_name, {'form': form})
    
    
# class StoreResultView(View):
#     template_name = 'tabloide/pages/index.html'

#     def get(self, request, store, *args, **kwargs):
#         stores = Store.objects.filter(store=store)
#         context = {'stores': stores, 'selected_city': store}
#         return render(request, self.template_name, context)
