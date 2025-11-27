from django.contrib import admin
from .models import ContentSource


@admin.register(ContentSource)
class ContentSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'status', 'chunks_count', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('name',)

