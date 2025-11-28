"""
Learning progress models.
"""
import uuid
from django.db import models


class LearningProgress(models.Model):
    """Model for tracking learning progress"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=255)
    progress = models.FloatField()  # 0.0 to 1.0
    notes = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_learningprogress'
        indexes = [
            models.Index(fields=['topic']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.topic} - {self.progress * 100:.1f}%"

