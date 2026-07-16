from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'updated_date')
    list_filter = ('author', 'created_date')
    search_fields = ('title', 'author', 'content')
    prepopulated_fields = {'slug': ('title',)}
