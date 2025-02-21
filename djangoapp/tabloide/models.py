
from django.db import models
from utils.rands import slygify_new
from utils.images import resize_image
from utils.scraper import scrape_product
from django.contrib.auth.models import User
from django_summernote.models import AbstractAttachment
from django.urls import reverse
from django.core.exceptions import ValidationError



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
            
class Product(models.Model):
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        
    objects = PostManager()
    pk = models.IntegerField(
        verbose_name='Código',
        name='Código',
        primary_key=True,
        unique=True,
        editable=True,
        serialize=False,
        blank=False,
        null=False,
        default=None,
    )
    title = models.CharField(max_length=50, verbose_name='Produto')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        default=None,
        blank=False,
        null=False,
    )
    excerpt = models.CharField(max_length=150, verbose_name='Descrição curta')
    cover = models.URLField(max_length=255, blank=True, null=True, default='')
    vitrine_link = models.URLField(blank=True, default='', null=True, max_length=255)
    is_published = models.BooleanField(
        default=True,
        help_text='Esse campo deve ser marcado para tornar o post publico',
    )
    old_price = models.FloatField(verbose_name='Preço De:')
    new_price = models.FloatField(verbose_name='Preço Por:')    
    offer_validity = models.DateField(
        verbose_name='Validade da oferta',
        blank=True,
        null=True,
        editable=True,
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
        Category, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name='Categoria'
    )
    tags = models.ManyToManyField(Tag, blank=True, default='')
    
    def format_brazilian_decimal(self,value):
        """
        Formats decimal number to Brazilian standard
        Example: 1234.56 -> 1.234,56
        """
        if not value:
            return '0,00'
        
        # Convert to string with 2 decimal places
        formatted = '{:.2f}'.format(float(value))
        
        # Split integer and decimal parts
        integer_part, decimal_part = formatted.split('.')
        
        # Add thousand separators
        integer_part = '{:,}'.format(int(integer_part)).replace(',', '.')
        
        # Join with Brazilian decimal separator
        return f'{integer_part},{decimal_part}'
        
    def get_old_price(self):
        value = self.old_price
        return self.format_brazilian_decimal(value)
    
    def get_new_price(self):
        value = self.new_price
        return self.format_brazilian_decimal(value)
    
    def installment_price(self):
        value = round(self.new_price / 10, 2)
        return self.format_brazilian_decimal(value)
    
    def percentage_discount(self):
        value = round(100 - (self.new_price / self.old_price * 100), 2) 
        return self.format_brazilian_decimal(value) + '%'
    
    def fees(self):
        value =  round(self.new_price / 10 * 12, 2)
        return self.format_brazilian_decimal(value)

    def get_absolute_url(self):
        if not self.is_published:
            return reverse("tabloide:index")
        return reverse("tabloide:product", args=(self.slug,))
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if not self._state.adding and self.pk != self.__original_pk:
            raise ValidationError({'Código': 'O valor do Código não pode ser alterado após a criação.'})
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_pk = self.pk
        return super().__init__(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        self.clean()
        self.cover = scrape_product(self.vitrine_link).get('img')

        if not self.slug:
            self.slug = slygify_new(self.title, 5)
   
        super_save = super().save(*args, **kwargs)
        return super_save
    
class Store(models.Model):
    class Meta:
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'

    objects = PostManager()
    number_store = models.IntegerField(verbose_name='Numero da Loja')
    title = models.CharField(max_length=50, verbose_name='Nome da Loja')
    phone_number = models.CharField(verbose_name='WhatsApp', max_length=11, blank=True, null=True, default='')
    text = models.TextField(max_length=255, verbose_name='Mensagem WhatsApp', blank=True, null=True, default='Estou interessado no produto: ')
    store_manager = models.CharField(max_length=100, verbose_name='Gerente')
    
    def whatsapp(self, text = None):
        number = f'55{str(self.phone_number)}'
                
        if text is None: text = f"Estou interessado no produto {self.title}."
        else: text = f"{text} {self.title}. "
        
        link = f"https://wa.me/{number}?text={text.replace(' ', '%20')}"
        return link
    
    def __str__(self):
        return self.title
    
