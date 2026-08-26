from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class Ticket(models.Model):

    class Status(models.TextChoices):

        OPEN = "OPEN", "Open"

        IN_PROGRESS = (
            "IN_PROGRESS",
            "In Progress",
        )

        RESOLVED = (
            "RESOLVED",
            "Resolved",
        )

        CLOSED = (
            "CLOSED",
            "Closed",
        )

    class Priority(models.TextChoices):

        LOW = "LOW", "Low"

        MEDIUM = (
            "MEDIUM",
            "Medium",
        )

        HIGH = "HIGH", "High"

        CRITICAL = (
            "CRITICAL",
            "Critical",
        )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requested_tickets",
    )

    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="tickets",
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    sla_due_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    first_response_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def is_sla_breached(self):

        if not self.sla_due_at:
            return False

        if self.resolved_at:
            return (
                self.resolved_at
                > self.sla_due_at
            )

        return timezone.now() > self.sla_due_at

    def __str__(self):

        return (
            f"#{self.id} - "
            f"{self.title}"
        )


class Comment(models.Model):

    class CommentType(models.TextChoices):

        PUBLIC = (
            "PUBLIC",
            "Public",
        )

        INTERNAL = (
            "INTERNAL",
            "Internal",
        )

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_comments",
    )

    content = models.TextField()

    comment_type = models.CharField(
        max_length=20,
        choices=CommentType.choices,
        default=CommentType.PUBLIC,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):

        return (
            f"Comment #{self.id} - "
            f"Ticket #{self.ticket.id}"
        )


class Attachment(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_attachments",
    )

    file = models.FileField(
        upload_to="ticket_attachments/"
    )

    original_filename = models.CharField(
        max_length=255,
    )

    file_size = models.PositiveIntegerField()

    content_type = models.CharField(
        max_length=100,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return self.original_filename


class TicketEvent(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="events",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ticket_events",
    )

    action = models.CharField(
        max_length=100,
    )

    old_value = models.JSONField(
        null=True,
        blank=True,
    )

    new_value = models.JSONField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at"
        ]

    def __str__(self):

        return (
            f"{self.action} - "
            f"Ticket #{self.ticket.id}"
        )