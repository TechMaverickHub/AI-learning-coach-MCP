"""
Digest models.
"""
import uuid
from django.db import models


class Digest(models.Model):
    """Model for daily learning digests"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generated_at = models.DateTimeField(auto_now_add=True)
    content = models.JSONField()
    ragas_score = models.FloatField(null=True, blank=True)
    user_feedback = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    
    class Meta:
        db_table = 'digest_digest'
        indexes = [
            models.Index(fields=['-generated_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Digest {self.id} - {self.generated_at}"

