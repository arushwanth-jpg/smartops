from django.db import models
class WebhookEvent(models.Model):

    STATUS_CHOICES = (
        ("received", "Received"),
        ("processing", "Processing"),
        ("processed", "Processed"),
        ("failed", "Failed"),
    )

    event_id = models.CharField(
        max_length=255,
        unique=True,
    )

    event_type = models.CharField(
        max_length=255,
    )

    source = models.CharField(
        max_length=100,
    )

    payload = models.JSONField(
        default=dict,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="received",
    )

    retry_count = models.PositiveIntegerField(
        default=0,
    )

    error_message = models.TextField(
        blank=True,
        null=True,
    )

    received_at = models.DateTimeField(
        auto_now_add=True,
    )

    processed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.source} - {self.event_type}"


class IntegrationLog(models.Model):

    STATUS_CHOICES = (
        ("success", "Success"),
        ("failed", "Failed"),
    )

    service = models.CharField(
        max_length=100,
    )

    endpoint = models.URLField(
        blank=True,
        null=True,
    )

    method = models.CharField(
        max_length=20,
        default="POST",
    )

    request_payload = models.JSONField(
        default=dict,
        blank=True,
    )

    response_payload = models.JSONField(
        default=dict,
        blank=True,
    )

    status_code = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    error_message = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.service} - {self.status}"
