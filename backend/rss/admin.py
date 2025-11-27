from django.contrib import admin
from .models import RSSFeed, RSSArticle


@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'feed_url', 'last_fetched', 'created_at')
    search_fields = ('name', 'feed_url')


@admin.register(RSSArticle)
class RSSArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'feed', 'published_at', 'indexed_at')
    list_filter = ('feed', 'published_at')
    search_fields = ('title', 'url')

