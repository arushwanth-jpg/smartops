from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from users.models import User

from .models import Category, Comment, Tag, Ticket, TicketEvent
from .permissions import IsAdminOrAgent
from .serializer import (
    TicketSerializer,
    CommentSerializer,
    CategorySerializer,
    TagSerializer,
    TicketAssignSerializer,
    TicketTransitionSerializer,
)


class TicketViewSet(viewsets.ModelViewSet):

    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # ADMIN can see all tickets
        if user.role == "ADMIN":
            return Ticket.objects.all().select_related(
                "requester",
                "assigned_agent",
                "category",
            )

        # AGENT can see assigned tickets
        # and tickets from their team
        if user.role == "AGENT":
            return Ticket.objects.filter(
                Q(assigned_agent=user)
                | Q(requester__team=user.team)
            ).select_related(
                "requester",
                "assigned_agent",
                "category",
            )

        # Normal users can only see their own tickets
        return Ticket.objects.filter(
            requester=user
        ).select_related(
            "requester",
            "assigned_agent",
            "category",
        )

    # ==========================================================
    # ASSIGN TICKET
    # ==========================================================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrAgent],
    )
    def assign(self, request, pk=None):
        """
        Assign a ticket to an agent.
        """

        ticket = self.get_object()

        serializer = TicketAssignSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        agent_id = serializer.validated_data["agent_id"]

        # Check whether the user exists and is an agent
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

        # Store previous agent
        old_agent = ticket.assigned_agent

        # Assign new agent
        ticket.assigned_agent = agent

        ticket.save(
            update_fields=[
                "assigned_agent",
                "updated_at",
            ]
        )

        # Create audit event
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
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    # ==========================================================
    # STATUS TRANSITION
    # ==========================================================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminOrAgent],
    )
    def transition(self, request, pk=None):
        """
        Change the status of a ticket.

        Allowed flow:

        OPEN
          ↓
        IN_PROGRESS
          ↓
        RESOLVED
          ↓
        CLOSED
        """

        ticket = self.get_object()

        serializer = TicketTransitionSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        new_status = serializer.validated_data["status"]

        # ------------------------------------------------------
        # Allowed status transitions
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # Validate transition
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # Update status
        # ------------------------------------------------------

        ticket.status = new_status

        # ------------------------------------------------------
        # Set resolved timestamp
        # ------------------------------------------------------

        if new_status == Ticket.Status.RESOLVED:
            ticket.resolved_at = timezone.now()

        # ------------------------------------------------------
        # Set closed timestamp
        # ------------------------------------------------------

        if new_status == Ticket.Status.CLOSED:
            ticket.closed_at = timezone.now()

        # Save ticket
        ticket.save()

        # ------------------------------------------------------
        # Create audit event
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # Return updated ticket
        # ------------------------------------------------------

        return Response(
            TicketSerializer(
                ticket,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
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
    permission_classes = [IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    
    