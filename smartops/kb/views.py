from django.db import transaction
from django.utils import timezone

from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    KBArticle,
    KBArticleVersion,
    TicketKBLink,
)

from .permissions import (
    IsAdminOrAgentOrReadOnly,
)

from .serializers import (
    KBArticleSerializer,
    KBArticleVersionSerializer,
    TicketKBLinkSerializer,
)


class KBArticleViewSet(
    viewsets.ModelViewSet
):

    queryset = KBArticle.objects.select_related(
        "author"
    ).all()

    serializer_class = KBArticleSerializer

    permission_classes = [
        IsAdminOrAgentOrReadOnly
    ]

    search_fields = [
        "title",
        "content",
    ]

    filterset_fields = [
        "status",
        "author",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "published_at",
    ]

    ordering = [
        "-created_at"
    ]

    def get_queryset(self):

        queryset = self.queryset

        user = self.request.user

        # Admin and Agent can see all articles
        if (
            user.is_authenticated
            and user.role in [
                "ADMIN",
                "AGENT",
            ]
        ):
            return queryset

        # Normal users only see published articles
        return queryset.filter(
            status=KBArticle.Status.PUBLISHED
        )

    def perform_create(
        self,
        serializer,
    ):

        with transaction.atomic():

            article = serializer.save(
                author=self.request.user
            )

            # Create initial version
            KBArticleVersion.objects.create(
                article=article,
                version_number=1,
                title=article.title,
                content=article.content,
                created_by=self.request.user,
            )

    def perform_update(
        self,
        serializer,
    ):

        with transaction.atomic():

            # Lock article while updating
            article = (
                KBArticle.objects
                .select_for_update()
                .get(
                    pk=serializer.instance.pk
                )
            )

            old_title = article.title
            old_content = article.content

            # Update locked instance
            serializer.instance = article

            article = serializer.save()

            # Create version only when
            # title or content changes
            content_changed = (
                old_title != article.title
                or
                old_content != article.content
            )

            if not content_changed:
                return

            last_version = (
                article.versions
                .order_by(
                    "-version_number"
                )
                .first()
            )

            if last_version:
                next_version = (
                    last_version.version_number
                    + 1
                )
            else:
                next_version = 1

            KBArticleVersion.objects.create(
                article=article,
                version_number=next_version,
                title=article.title,
                content=article.content,
                created_by=self.request.user,
            )

    @action(
        detail=True,
        methods=["post"],
    )
    def publish(
        self,
        request,
        pk=None,
    ):

        with transaction.atomic():

            article = (
                KBArticle.objects
                .select_for_update()
                .get(
                    pk=self.get_object().pk
                )
            )

            # Prevent publishing twice
            if (
                article.status
                == KBArticle.Status.PUBLISHED
            ):

                return Response(
                    {
                        "detail":
                        "Article is already published."
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            article.status = (
                KBArticle.Status.PUBLISHED
            )

            # Save publication time
            article.published_at = (
                timezone.now()
            )

            article.save(
                update_fields=[
                    "status",
                    "published_at",
                    "updated_at",
                ]
            )

        return Response(
            KBArticleSerializer(
                article,
                context={
                    "request": request
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def archive(
        self,
        request,
        pk=None,
    ):

        with transaction.atomic():

            article = (
                KBArticle.objects
                .select_for_update()
                .get(
                    pk=self.get_object().pk
                )
            )

            # Prevent archiving twice
            if (
                article.status
                == KBArticle.Status.ARCHIVED
            ):

                return Response(
                    {
                        "detail":
                        "Article is already archived."
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            article.status = (
                KBArticle.Status.ARCHIVED
            )

            article.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            KBArticleSerializer(
                article,
                context={
                    "request": request
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
    )
    def versions(
        self,
        request,
        pk=None,
    ):

        article = self.get_object()

        versions = (
            article.versions.all()
        )

        serializer = (
            KBArticleVersionSerializer(
                versions,
                many=True,
            )
        )

        return Response(
            serializer.data
        )


class TicketKBLinkViewSet(
    viewsets.ModelViewSet
):

    queryset = (
        TicketKBLink.objects
        .select_related(
            "ticket",
            "article",
            "linked_by",
        )
        .all()
    )

    serializer_class = (
        TicketKBLinkSerializer
    )

    permission_classes = [
        IsAdminOrAgentOrReadOnly
    ]

    filterset_fields = [
        "ticket",
        "article",
    ]

    def perform_create(
        self,
        serializer,
    ):

        serializer.save(
            linked_by=self.request.user
        )