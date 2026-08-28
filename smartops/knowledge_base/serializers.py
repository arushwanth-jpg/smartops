from django.utils.html import strip_tags
from rest_framework import serializers

import markdown

from .models import (
    KBArticle,
    KBArticleVersion,
    TicketKBLink,
)



class KBArticleSerializer(serializers.ModelSerializer):

    rendered_content = serializers.SerializerMethodField()

    class Meta:
        model = KBArticle

        fields = [
            "id",
            "title",
            "slug",
            "content",
            "rendered_content",
            "summary",
            "status",
            "category",
            "tags",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "published_at",
        ]

        read_only_fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "published_at",
            "rendered_content",
        ]

    def get_rendered_content(self, obj):
        html = markdown.markdown(
            obj.content,
            extensions=[
                "fenced_code",
                "tables",
            ],
        )

        return html


class KBArticleVersionSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = KBArticleVersion

        fields = [
            "id",
            "article",
            "version_number",
            "title",
            "content",
            "summary",
            "category",
            "tags",
            "status",
            "changed_by",
            "created_at",
        ]

        read_only_fields = [
            "version_number",
            "changed_by",
            "created_at",
        ]


class TicketKBLinkSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = TicketKBLink

        fields = [
            "id",
            "ticket",
            "article",
            "linked_by",
            "created_at",
        ]

        read_only_fields = [
            "linked_by",
            "created_at",
        ]