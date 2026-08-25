from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category, Comment, Tag, Ticket
from .serializer import CategorySerializer,CommentSerializer,TagSerializer,TicketSerializer


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
