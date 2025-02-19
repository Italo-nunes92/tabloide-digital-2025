
from django.db import models
from utils.rands import slygify_new
from django.contrib.auth.models import User
from utils.images import resize_image
from django_summernote.models import AbstractAttachment
from django.urls import reverse



class PostAttachment(AbstractAttachment):
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        current_file_name = str(self.file.name)
        super_save = super().save(*args, **kwargs)
        file_changed = False
        if self.file:
            file_changed = current_file_name != self.file.name
        if file_changed:
            resize_image(self.file, 900, True, 70)
        return super_save

class Tag(models.Model):
    class Meta:
        
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        max_length=50, 
        unique=True,
        default=None,
        blank=True,
        null=True,
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slygify_new(self.name, 5)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
    name = models.CharField(max_length=50)
    slug = models.SlugField(
        max_length=50, 
        unique=True,
        default=None,
        blank=True,
        null=True,
    )
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slygify_new(self.name, 5)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Page(models.Model):
    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    title = models.CharField(max_length=50)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        default="",
        blank=True,
        null=False,
    )
    is_published = models.BooleanField(
        default=True,
        help_text='Esse campo deve ser marcado para tornar a página publica',
        
    )
    content = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slygify_new(self.title, 5)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
class PostManager(models.Manager):
    def get_published(self):
        return self\
            .filter(is_published=True)\
            .order_by('-pk')
            
class Post(models.Model):
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        
    objects = PostManager()
    
    title = models.CharField(max_length=50)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        default="",
        blank=True,
        null=False,
    )
    
    excerpt = models.CharField(max_length=150)
    vitrine_link = models.URLField(blank=True, default='', null=True, max_length=255)
    is_published = models.BooleanField(
        default=True,
        help_text='Esse campo deve ser marcado para tornar o post publico',
    )
    content = models.TextField()
    cover = models.ImageField(upload_to='posts/%Y/%m/', blank=True, default='')
    cover_in_post_content = models.BooleanField(
        default=True,
        help_text='Exibir a capa dentro do post?',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='post_created_by',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='post_updated_by',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, default=None,
    )
    tags = models.ManyToManyField(Tag, blank=True, default='')
    
    def get_absolute_url(self):
        if not self.is_published:
            return reverse("tabloide:index")
        
        return reverse("tabloide:post", args=(self.slug,))
    
    def whatsapp(self):
        number = '5517996753874'
        
        text = f"Estou interessado no produto {self.title}."
        
        link = f"https://wa.me/{number}?text={text.replace(' ', '%20')}"
        return link
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slygify_new(self.title, 5)

        corrent_cover_name = str(self.cover.name)
        super_save = super().save(*args, **kwargs)
        cover_changed = False
        if corrent_cover_name != self.cover.name:
            cover_changed = True
        if cover_changed: resize_image(self.cover, 900)  
        return super_save
    