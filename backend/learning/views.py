"""
Views for learning app.
"""
from rest_framework import viewsets
from .models import LearningProgress
from .serializers import LearningProgressSerializer


class LearningProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for LearningProgress"""
    queryset = LearningProgress.objects.all()
    serializer_class = LearningProgressSerializer

