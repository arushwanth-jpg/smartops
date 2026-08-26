from rest_framework import serializers
from .models import (
    KBArticle,
    KBArticleVersion,
    TicketKBLink
)


class KBArticleSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = KBArticle

        fields = [
            "id",
            "title",
            "slug",
            "content",
            "status",
            "author",
            "created_at",
            "updated_at",
            "published_at",
        ]

        read_only_fields = [
            "author",
            "created_at",
            "updated_at",
            "published_at",
        ]


class KBArticleVersionSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = KBArticleVersion

        fields = "__all__"


class TicketKBLinkSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = TicketKBLink

        fields = "__all__"