from django.db.models import Q
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    KBArticle,
    KBArticleVersion,
    TicketKBLink,
)

from .serializers import (
    KBArticleSerializer,
    KBArticleVersionSerializer,
    TicketKBLinkSerializer,
)



class KBArticleViewSet(viewsets.ModelViewSet):

    queryset = KBArticle.objects.all()

    serializer_class = KBArticleSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def perform_create(self, serializer):

        article = serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

        KBArticleVersion.objects.create(
            article=article,
            version_number=1,
            title=article.title,
            content=article.content,
            summary=article.summary,
            category=article.category,
            tags=article.tags,
            status=article.status,
            changed_by=self.request.user,
        )

    def perform_update(self, serializer):

        old_article = self.get_object()

        article = serializer.save(
            updated_by=self.request.user,
        )

        latest_version = (
            KBArticleVersion.objects
            .filter(article=article)
            .order_by("-version_number")
            .first()
        )

        next_version = (
            latest_version.version_number + 1
            if latest_version
            else 1
        )

        KBArticleVersion.objects.create(
            article=article,
            version_number=next_version,
            title=article.title,
            content=article.content,
            summary=article.summary,
            category=article.category,
            tags=article.tags,
            status=article.status,
            changed_by=self.request.user,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def publish(self, request, pk=None):

        article = self.get_object()

        article.status = "published"
        article.published_at = timezone.now()
        article.updated_by = request.user

        article.save()

        return Response(
            {
                "message": "Article published successfully",
                "article_id": article.id,
                "status": article.status,
            }
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def unpublish(self, request, pk=None):

        article = self.get_object()

        article.status = "draft"
        article.published_at = None
        article.updated_by = request.user

        article.save()

        return Response(
            {
                "message": "Article unpublished successfully",
                "article_id": article.id,
                "status": article.status,
            }
        )

    @action(
        detail=True,
        methods=["get"],
    )
    def versions(self, request, pk=None):

        article = self.get_object()

        versions = article.versions.all()

        serializer = KBArticleVersionSerializer(
            versions,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
    )
    def search(self, request):

        query = request.query_params.get(
            "q",
            "",
        ).strip()

        if not query:
            return Response(
                {
                    "error": "Search query is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        articles = KBArticle.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(summary__icontains=query)
            | Q(category__icontains=query)
        ).distinct()

        serializer = self.get_serializer(
            articles,
            many=True,
        )

        return Response(
            {
                "query": query,
                "count": articles.count(),
                "results": serializer.data,
            }
        )


class TicketKBLinkViewSet(viewsets.ModelViewSet):

    queryset = TicketKBLink.objects.all()

    serializer_class = TicketKBLinkSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def perform_create(self, serializer):

        serializer.save(
            linked_by=self.request.user
        )
