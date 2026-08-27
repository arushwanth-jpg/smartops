from rest_framework import serializers

from .models import (
    KBArticle,
    KBArticleVersion,
    TicketKBLink,   
    
)


class KBArticleVersionSerializer(
    serializers.ModelSerializer
):

    created_by_name = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = KBArticleVersion

        fields = [
            "id",
            "article",
            "version_number",
            "title",
            "content",
            "created_by",
            "created_by_name",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "article",
            "version_number",
            "created_by",
            "created_by_name",
            "created_at",
        ]


class KBArticleSerializer(
    serializers.ModelSerializer
):

    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = KBArticle

        fields = [
            "id",
            "title",
            "slug",
            "content",

            "author",
            "author_name",

            "status",

            "created_at",
            "updated_at",
            "published_at",
        ]

        read_only_fields = [
            "id",
            "author",
            "author_name",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        ]


class TicketKBLinkSerializer(
    serializers.ModelSerializer
):

    article_title = serializers.CharField(
        source="article.title",
        read_only=True,
    )

    linked_by_name = serializers.CharField(
        source="linked_by.username",
        read_only=True,
    )

    class Meta:
        model = TicketKBLink

        fields = [
            "id",
            "ticket",
            "article",
            "article_title",

            "linked_by",
            "linked_by_name",

            "created_at",
        ]

        read_only_fields = [
            "id",
            "linked_by",
            "linked_by_name",
            "article_title",
            "created_at",
        ]