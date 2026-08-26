from django.db import models
from django.conf import settings


class KBArticle(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True
    )

    content = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="kb_articles"
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
        related_name="versions"
    )

    version_number = models.PositiveIntegerField()

    title = models.CharField(
        max_length=255
    )

    content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "article",
            "version_number"
        )

    def __str__(self):
        return f"{self.article.title} v{self.version_number}"


class TicketKBLink(models.Model):

    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="kb_links"
    )

    article = models.ForeignKey(
        KBArticle,
        on_delete=models.CASCADE,
        related_name="ticket_links"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "ticket",
            "article"
        )