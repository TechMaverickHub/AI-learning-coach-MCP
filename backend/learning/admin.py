from django.contrib import admin
from .models import LearningProgress


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ('topic', 'progress', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('topic',)

