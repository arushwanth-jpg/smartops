from django.conf import settings
from django.db import models


class KBArticle(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True,
    )

    content = models.TextField()

    summary = models.TextField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    tags = models.JSONField(
        default=list,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="kb_articles_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kb_articles_updated",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-updated_at"]

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
        max_length=255,
    )

    content = models.TextField()

    summary = models.TextField(
        blank=True,
        null=True,
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    tags = models.JSONField(
        default=list,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
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
        return f"{self.article.title} - v{self.version_number}"


class TicketKBLink(models.Model):

    ticket = models.ForeignKey(
        "tickets.Ticket",
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
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "ticket",
                    "article",
                ],
                name="unique_ticket_kb_link",
            )
        ]

    def __str__(self):
        return f"{self.ticket} -> {self.article}"
