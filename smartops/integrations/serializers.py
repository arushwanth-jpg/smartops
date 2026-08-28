from rest_framework import serializers

from .models import (
    WebhookEvent,
    IntegrationLog,
)


class WebhookEventSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WebhookEvent

        fields = [
            "id",
            "event_id",
            "event_type",
            "source",
            "payload",
            "status",
            "retry_count",
            "error_message",
            "received_at",
            "processed_at",
        ]

        read_only_fields = [
            "status",
            "retry_count",
            "error_message",
            "received_at",
            "processed_at",
        ]


class IntegrationLogSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = IntegrationLog

        fields = [
            "id",
            "service",
            "endpoint",
            "method",
            "request_payload",
            "response_payload",
            "status_code",
            "status",
            "error_message",
            "created_at",
        ]

        read_only_fields = [
            "created_at",
        ]