from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from users.models import User

from .models import (
    Category,
    Comment,
    Tag,
    Ticket,
    TicketEvent,
)
from .permissions import IsAdminOrAgent
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

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Ticket.objects.all().select_related(
                "requester",
                "assigned_agent",
                "category",
            )


        if user.role == "AGENT":
            return Ticket.objects.filter(
                Q(assigned_agent=user)
                | Q(requester__team=user.team)
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

        agent_id = serializer.validated_data["agent_id"]

        # Find agent
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

        new_status = serializer.validated_data["status"]

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
            []
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

        comment = serializer.save(
            ticket=ticket,
            author=request.user,
        )

     
        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            event_type="COMMENT_ADDED",
            new_value=str(comment.id),
        )

        return Response(
            CommentSerializer(comment).data,
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

        attachment = serializer.save(
            ticket=ticket,
            uploaded_by=request.user,
        )

     
        TicketEvent.objects.create(
            ticket=ticket,
            actor=request.user,
            event_type="ATTACHMENT_ADDED",
            new_value=str(attachment.id),
        )

        return Response(
            AttachmentSerializer(
                attachment
            ).data,
            status=status.HTTP_201_CREATED,
        )


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Comment.objects.filter(
            ticket_id=self.kwargs["ticket_pk"]
        )

    def perform_create(self, serializer):

        serializer.save(
            author=self.request.user
        )


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer

    permission_classes = [
        IsAuthenticated
    ]


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()

    serializer_class = TagSerializer

    permission_classes = [
        IsAuthenticated
    ]