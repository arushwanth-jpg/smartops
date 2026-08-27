from django.conf import settings
from django.db import models

from tickets.models import Ticket


class KBArticle(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        ARCHIVED = "ARCHIVED", "Archived"

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=255,
        unique=True
    )

    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="kb_articles",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class KBArticleVersion(models.Model):

    article = models.ForeignKey(
        KBArticle,
        on_delete=models.CASCADE,
        related_name="versions",
    )

    version_number = models.PositiveIntegerField()

    title = models.CharField(
        max_length=255
    )

    content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="kb_versions",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-version_number"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "article",
                    "version_number",
                ],
                name="unique_article_version",
            )
        ]

    def __str__(self):
        return (
            f"{self.article.title} "
            f"- Version {self.version_number}"
        )


class TicketKBLink(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="kb_links",
    )

    article = models.ForeignKey(
        KBArticle,
        on_delete=models.CASCADE,
        related_name="ticket_links",
    )

    linked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="kb_ticket_links",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "ticket",
                    "article",
                ],
                name="unique_ticket_article_link",
            )
        ]

    def __str__(self):
        return (
            f"Ticket #{self.ticket.id} "
            f"→ {self.article.title}"
        )
