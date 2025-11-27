"""
Serializers for learning app.
"""
from rest_framework import serializers
from .models import LearningProgress


class LearningProgressSerializer(serializers.ModelSerializer):
    """Serializer for LearningProgress model"""
    
    class Meta:
        model = LearningProgress
        fields = ['id', 'topic', 'progress', 'notes', 'updated_at', 
                  'memory_id', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

