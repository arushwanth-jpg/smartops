
from django.contrib import admin

from .models import (
    IntegrationLog,
    WebhookEvent,
)


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):

    list_display = [
        "event_id",
        "event_type",
        "source",
        "status",
        "retry_count",
        "received_at",
    ]

    list_filter = [
        "status",
        "source",
        "event_type",
    ]

    search_fields = [
        "event_id",
        "event_type",
        "source",
    ]


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):

    list_display = [
        "service",
        "method",
        "status_code",
        "status",
        "created_at",
    ]

    list_filter = [
        "service",
        "status",
        "method",
    ]