"""
Serializers for content app.
"""
from rest_framework import serializers
from .models import ContentSource


class ContentSourceSerializer(serializers.ModelSerializer):
    """Serializer for ContentSource model"""
    
    class Meta:
        model = ContentSource
        fields = ['id', 'name', 'type', 'source_url', 'file', 'created_at', 
                  'updated_at', 'status', 'chunks_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'chunks_count']

