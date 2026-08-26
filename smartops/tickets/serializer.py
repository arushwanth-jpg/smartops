from rest_framework import serializers

from .services import calculate_sla_due_at

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
            "ticket",
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
            "ticket",
            "uploaded_by",
            "original_filename",
            "file_size",
            "content_type",
            "uploaded_at",
        ]

    def validate_file(self, value):

        max_size = 10 * 1024 * 1024

        if value.size > max_size:

            raise serializers.ValidationError(
                "File size cannot exceed 10 MB."
            )

        allowed_types = [
            "image/jpeg",
            "image/png",
            "application/pdf",
            "text/plain",
        ]

        if value.content_type not in allowed_types:

            raise serializers.ValidationError(
                "Unsupported file type."
            )

        return value


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

    is_sla_breached = serializers.BooleanField(
        read_only=True
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
            "is_sla_breached",
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

            "assigned_agent",
            "assigned_agent_name",

            "category_name",
            "tags_data",

            "status",

            "sla_due_at",
            "is_sla_breached",
            "first_response_at",

            "resolved_at",
            "closed_at",

            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):

        request = self.context[
            "request"
        ]

        tags = validated_data.pop(
            "tags",
            [],
        )

        priority = validated_data.get(
            "priority",
            Ticket.Priority.MEDIUM,
        )

        ticket = Ticket.objects.create(
            requester=request.user,
            sla_due_at=calculate_sla_due_at(
                priority
            ),
            **validated_data,
        )

        if tags:
            ticket.tags.set(tags)

        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            action="CREATED",
            new_value={
                "status": ticket.status,
                "priority": ticket.priority,
                "sla_due_at": (
                    ticket.sla_due_at.isoformat()
                    if ticket.sla_due_at
                    else None
                ),
            },
        )

        return ticket


class TicketAssignSerializer(
    serializers.Serializer
):

    agent_id = serializers.IntegerField()


class TicketTransitionSerializer(
    serializers.Serializer
):

    status = serializers.ChoiceField(
        choices=Ticket.Status.choices
    )