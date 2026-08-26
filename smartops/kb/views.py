from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import KBArticle
from .serializers import KBArticleSerializer


class KBArticleViewSet(viewsets.ModelViewSet):

    queryset = KBArticle.objects.all()

    serializer_class = KBArticleSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def perform_create(self, serializer):

        serializer.save(
            author=self.request.user
        )