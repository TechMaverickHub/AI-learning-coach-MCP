from django.contrib import admin
from .models import Digest


@admin.register(Digest)
class DigestAdmin(admin.ModelAdmin):
    list_display = ('id', 'generated_at', 'ragas_score', 'status')
    list_filter = ('status', 'generated_at')
    readonly_fields = ('generated_at',)

