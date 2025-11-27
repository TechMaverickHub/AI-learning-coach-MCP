"""
Content management models.
"""
import uuid
from django.db import models


class ContentSource(models.Model):
    """Model for content sources (PDFs, notes, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)  # 'pdf', 'rss', 'note'
    source_url = models.URLField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')  # 'active', 'deleted'
    chunks_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'content_contentsource'
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.type})"

