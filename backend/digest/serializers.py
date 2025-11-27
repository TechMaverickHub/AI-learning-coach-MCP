"""
Serializers for digest app.
"""
from rest_framework import serializers
from .models import Digest


class DigestSerializer(serializers.ModelSerializer):
    """Serializer for Digest model"""
    
    class Meta:
        model = Digest
        fields = ['id', 'generated_at', 'content', 'ragas_score', 
                  'user_feedback', 'status']
        read_only_fields = ['id', 'generated_at']

