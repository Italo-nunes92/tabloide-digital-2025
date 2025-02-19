import requests
from bs4 import BeautifulSoup
from tabloide.models import Post
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic import ListView, DetailView

PER_PAGE = 9

class PostListView(ListView):
    template_name = 'tabloide/pages/index.html'
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published()
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': 'Home | ',
            }
        )
        return context

class CreatedByListView(PostListView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._temp_context = {}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self._temp_context['user']
        
        if user.first_name:
            page_title = f'{user.first_name} {user.last_name} | '
        else:
            page_title = f'{user.username} | '
        
        context.update({ 'page_title': page_title } )
        
        return context
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(created_by__pk=self._temp_context['user'].pk)
                
        return qs
    
    def get(self, request, *args, **kwargs):
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()
        
        if not user: raise Http404()
        
        self._temp_context.update({
            'user': user,
            'author_pk': author_pk
        })
        
        return super().get(request, *args, **kwargs)
    
class CategoryPostView(PostListView):
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
    
class TagListView(PostListView):
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
    
class SearchListView(PostListView):
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

class PostView(DetailView):
    model = Post
    template_name = 'tabloide/pages/post.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = self.get_object()
        page_title = f'{post.title} | '
        ctx.update(
            {
                'page_title': page_title,
            }
        )
        return ctx
    
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
    

def post(request, slug):
    post = Post.objects.get_published().filter(slug=slug).first()
    
    if post is None:
            raise Http404()
        
    context = {}
    if post.vitrine_link:
        html_content = get_content(post.vitrine_link)
        soup = BeautifulSoup(html_content, 'html.parser', from_encoding='utf-8')
                
        title = soup.select_one('.titulo')
        description = soup.select_one('.product-details')
        img = soup.select_one('.MagicZoomPlus').find('img')['src']    
        
        
    
        page_title = f'{post.title} - Produto | '    
        context = {
            'title_v': title.text.strip(),
            'description_v': f"""{description}""".replace('','"',-1).replace('','"',-1),
            'img_v': f'https:{img}',
            'post': post,
            'page_title': page_title,
        } 
    

    return render(
        request,
        'tabloide/pages/post.html',
        context=context
    )
    
def get_content(page):
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    LANGUAGE = 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'{page}').text
    
    html_content = html_content.encode('utf-8', errors='ignore').decode('utf-8')
    
    return html_content
