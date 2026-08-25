from rest_framework import serializers

from .models import (
    Attachment,
    Category,
    Comment,
    Tag,
    Ticket,
    TicketEvent,
)

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):

    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = Comment

        fields = [
            "id",
            "ticket",
            "author",
            "author_name",
            "content",
            "comment_type",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "author",
            "author_name",
            "created_at",
            "updated_at",
        ]


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment

        fields = [
            "id",
            "ticket",
            "uploaded_by",
            "file",
            "original_filename",
            "file_size",
            "content_type",
            "uploaded_at",
        ]

        read_only_fields = [
            "id",
            "uploaded_by",
            "file_size",
            "content_type",
            "uploaded_at",
        ]


class TicketSerializer(serializers.ModelSerializer):

    requester_name = serializers.CharField(
        source="requester.username",
        read_only=True,
    )

    assigned_agent_name = serializers.CharField(
        source="assigned_agent.username",
        read_only=True,
        allow_null=True,
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
        allow_null=True,
    )

    tags_data = TagSerializer(
        source="tags",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Ticket

        fields = [
            "id",
            "title",
            "description",
            "requester",
            "requester_name",
            "assigned_agent",
            "assigned_agent_name",
            "category",
            "category_name",
            "tags",
            "tags_data",
            "priority",
            "status",
            "sla_due_at",
            "first_response_at",
            "resolved_at",
            "closed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "requester",
            "requester_name",
            "assigned_agent_name",
            "category_name",
            "tags_data",
            "sla_due_at",
            "first_response_at",
            "resolved_at",
            "closed_at",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        ticket = Ticket.objects.create(
            requester=request.user,
            **validated_data,
        )

        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            action="CREATED",
            new_value={
                "status": ticket.status,
                "priority": ticket.priority,
            },
        )

        return ticket