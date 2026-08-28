from django.shortcuts import render

# Create your views here.
import uuid

from django.utils import timezone

from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import (
    action,
    api_view,
    permission_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from .models import (
    IntegrationLog,
    WebhookEvent,
)

from .serializers import (
    IntegrationLogSerializer,
    WebhookEventSerializer,
)

from .tasks import process_webhook


@api_view(["POST"])
@permission_classes([AllowAny])
def webhook_receiver(request):

    payload = request.data

    event_type = request.headers.get(
        "X-Event-Type",
        "unknown",
    )

    event_id = request.headers.get(
        "X-Event-ID"
    )

    if not event_id:

        event_id = str(
            uuid.uuid4()
        )

    webhook, created = (
        WebhookEvent.objects.get_or_create(
            event_id=event_id,
            defaults={
                "event_type": event_type,
                "source": "external",
                "payload": payload,
            },
        )
    )

    if not created:

        return Response(
            {
                "message": "Webhook already received",
                "event_id": event_id,
            },
            status=status.HTTP_200_OK,
        )

    process_webhook.delay(
        webhook.id
    )

    return Response(
        {
            "message": "Webhook received",
            "event_id": event_id,
            "status": "queued",
        },
        status=status.HTTP_202_ACCEPTED,
    )


class WebhookEventViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = WebhookEvent.objects.all()

    serializer_class = WebhookEventSerializer

    permission_classes = [
        IsAuthenticated
    ]


class IntegrationLogViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = IntegrationLog.objects.all()

    serializer_class = IntegrationLogSerializer

    permission_classes = [
        IsAuthenticated
    ]