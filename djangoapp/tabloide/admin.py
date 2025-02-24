from django.contrib import admin
from tabloide.models import Tag, Category, Page, Product, Store
from django_summernote.admin import SummernoteModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

# Register your models here.
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'slug',
    list_display_links = 'name',
    search_fields = 'id', 'name', 'slug',
    list_per_page = 10
    ordering = '-id',
    prepopulated_fields = {
        'slug': ('name',)
    }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'slug',
    list_display_links = 'name',
    search_fields = 'id', 'name', 'slug',
    list_per_page = 10
    ordering = '-id',
    prepopulated_fields = {
        'slug': ('name',)
    }
    actions = 'link'

@admin.register(Page)
class PageAdmin(SummernoteModelAdmin):
    summernote_fields = 'content',
    list_display = 'id', 'title', 'slug', 'is_published',
    list_display_links = 'title',
    search_fields = 'id', 'title', 'slug', 'content',
    list_per_page = 50
    list_filter = 'is_published',
    list_editable = 'is_published',
    ordering = '-id',
    prepopulated_fields = {
        'slug': ('title',)
    }
    

@admin.register(Product)
class ProductAdmin(SummernoteModelAdmin):
    summernote_fields = 'content',
    list_display = 'pk', 'title', 'new_price', 'offer_validity', 'is_published',
    list_display_links = 'title',
    search_fields = 'pk', 'title', 'new_price', 'offer_validity', 'is_published',
    list_per_page = 50
    list_filter = 'is_published', 'category',
    list_editable = 'is_published', 'offer_validity',
    ordering = 'offer_validity',
    prepopulated_fields = {
        'slug': ('title',)
    }
    readonly_fields = 'created_at', 'updated_at','updated_by','created_by','link',
    autocomplete_fields = 'tags', 'category',
    
    hidden_fields = 'text_link',
    
    
    def link(self, obj):
        if not obj.pk:
            return '-'
        

        url_do_post = obj.get_absolute_url()
        link = mark_safe(f'<a href="{url_do_post}" target="_blank">{obj.title}</a>')
        return link
 
    def save_model(self, request, obj, form, change):
        print()
        
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user

        obj.save()
        
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = 'number_store', 'title', 'phone_number','store_manager',
    list_display_links = 'title',
    search_fields = 'number_store', 'title', 'phone_number','store_manager',
    list_per_page = 40
    ordering = 'pk',
    readonly_fields = 'text_link',
