from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User
from integrations.services import trigger_webhook

from .models import (
    Category,
    Comment,
    Tag,
    Ticket,
    TicketEvent,
)

from .permissions import (
    IsAdmin,
    IsAdminOrAgent,
)

from .serializer import (
    TicketSerializer,
    CommentSerializer,
    CategorySerializer,
    TagSerializer,
    TicketAssignSerializer,
    TicketTransitionSerializer,
    AttachmentSerializer,
)


class TicketViewSet(viewsets.ModelViewSet):

    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "status",
        "priority",
        "category",
        "assigned_agent",
    ]

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "priority",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):

        user = self.request.user

        if user.role == "ADMIN":
            return Ticket.objects.all().select_related(
                "requester",
                "assigned_agent",
                "category",
            )

        if user.role == "AGENT":

            query = Q(assigned_agent=user)

            if user.team:
                query |= Q(
                    requester__team=user.team
                )

            return Ticket.objects.filter(
                query
            ).select_related(
                "requester",
                "assigned_agent",
                "category",
            )

        return Ticket.objects.filter(
            requester=user
        ).select_related(
            "requester",
            "assigned_agent",
            "category",
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrAgent],
    )
    def assign(self, request, pk=None):

        ticket = self.get_object()

        serializer = TicketAssignSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        agent_id = serializer.validated_data[
            "agent_id"
        ]

        try:
            agent = User.objects.get(
                id=agent_id,
                role="AGENT",
            )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": "Agent not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        old_agent = ticket.assigned_agent

        ticket.assigned_agent = agent

        ticket.save(
            update_fields=[
                "assigned_agent",
                "updated_at",
            ]
        )

        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            action="ASSIGNED",
            old_value={
                "assigned_agent": (
                    old_agent.id
                    if old_agent
                    else None
                )
            },
            new_value={
                "assigned_agent": agent.id
            },
        )

        trigger_webhook(
            "TICKET_ASSIGNED",
            {
                "ticket": {
                    "id": ticket.id,
                    "title": ticket.title,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "assigned_agent_id": agent.id,
                    "assigned_agent": agent.username,
                }
            },
        )

        return Response(
            TicketSerializer(
                ticket,
                context={
                    "request": request
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrAgent],
    )
    def transition(self, request, pk=None):

        ticket = self.get_object()

        serializer = TicketTransitionSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data[
            "status"
        ]

        allowed_transitions = {
            Ticket.Status.OPEN: [
                Ticket.Status.IN_PROGRESS
            ],
            Ticket.Status.IN_PROGRESS: [
                Ticket.Status.RESOLVED
            ],
            Ticket.Status.RESOLVED: [
                Ticket.Status.CLOSED
            ],
            Ticket.Status.CLOSED: [],
        }

        current_status = ticket.status

        if new_status not in allowed_transitions.get(
            current_status,
            [],
        ):
            return Response(
                {
                    "detail": (
                        f"Invalid transition: "
                        f"{current_status} → {new_status}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.status = new_status

        if new_status == Ticket.Status.RESOLVED:
            ticket.resolved_at = timezone.now()

        if new_status == Ticket.Status.CLOSED:
            ticket.closed_at = timezone.now()

        ticket.save()

        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            action="STATUS_CHANGED",
            old_value={
                "status": current_status
            },
            new_value={
                "status": new_status
            },
        )

        trigger_webhook(
            "TICKET_STATUS_CHANGED",
            {
                "ticket": {
                    "id": ticket.id,
                    "title": ticket.title,
                    "priority": ticket.priority,
                    "old_status": current_status,
                    "status": new_status,
                }
            },
        )

        return Response(
            TicketSerializer(
                ticket,
                context={
                    "request": request
                },
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get", "post"],
    )
    def comments(self, request, pk=None):

        ticket = self.get_object()

        if request.method == "GET":

            if request.user.role == "REQUESTER":
                comments = ticket.comments.filter(
                    comment_type=Comment.CommentType.PUBLIC
                )
            else:
                comments = ticket.comments.all()

            serializer = CommentSerializer(
                comments,
                many=True,
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        serializer = CommentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        if (
            request.user.role == "REQUESTER"
            and serializer.validated_data.get(
                "comment_type"
            ) == Comment.CommentType.INTERNAL
        ):
            return Response(
                {
                    "detail": (
                        "Requesters cannot create "
                        "internal comments."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        comment = serializer.save(
            ticket=ticket,
            author=request.user,
        )

        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            action="COMMENT_ADDED",
            new_value={
                "comment_id": comment.id
            },
        )

        trigger_webhook(
            "COMMENT_ADDED",
            {
                "ticket": {
                    "id": ticket.id,
                    "title": ticket.title,
                },
                "comment": {
                    "id": comment.id,
                    "content": comment.content,
                    "comment_type": comment.comment_type,
                    "author_id": request.user.id,
                },
            },
        )

        return Response(
            CommentSerializer(
                comment
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def attachments(self, request, pk=None):

        ticket = self.get_object()

        serializer = AttachmentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        uploaded_file = serializer.validated_data[
            "file"
        ]

        attachment = serializer.save(
            ticket=ticket,
            uploaded_by=request.user,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            content_type=uploaded_file.content_type,
        )

        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            action="ATTACHMENT_ADDED",
            new_value={
                "attachment_id": attachment.id,
                "filename": attachment.original_filename,
            },
        )

        trigger_webhook(
            "ATTACHMENT_ADDED",
            {
                "ticket": {
                    "id": ticket.id,
                    "title": ticket.title,
                },
                "attachment": {
                    "id": attachment.id,
                    "filename": attachment.original_filename,
                    "file_size": attachment.file_size,
                    "content_type": attachment.content_type,
                },
            },
        )

        return Response(
            AttachmentSerializer(
                attachment
            ).data,
            status=status.HTTP_201_CREATED,
        )


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdmin]