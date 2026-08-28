from celery import shared_task
from django.utils import timezone

from .models import (
    IntegrationLog,
    WebhookEvent,
)


@shared_task(
    bind=True,
    max_retries=3,
)
def process_webhook(
    self,
    webhook_id,
):

    try:

        webhook = WebhookEvent.objects.get(
            id=webhook_id
        )

        webhook.status = "processing"
        webhook.save(
            update_fields=["status"]
        )

        payload = webhook.payload

        event_type = webhook.event_type

        # ----------------------------------
        # Process different event types
        # ----------------------------------

        if event_type == "ticket.created":

            process_ticket_created(
                payload
            )

        elif event_type == "ticket.updated":

            process_ticket_updated(
                payload
            )

        elif event_type == "ticket.closed":

            process_ticket_closed(
                payload
            )

        else:

            raise ValueError(
                f"Unsupported event type: {event_type}"
            )

        webhook.status = "processed"

        webhook.processed_at = timezone.now()

        webhook.save(
            update_fields=[
                "status",
                "processed_at",
            ]
        )

        return {
            "status": "processed",
            "webhook_id": webhook_id,
        }

    except Exception as exc:

        webhook = WebhookEvent.objects.get(
            id=webhook_id
        )

        webhook.retry_count += 1

        webhook.status = "failed"

        webhook.error_message = str(exc)

        webhook.save(
            update_fields=[
                "retry_count",
                "status",
                "error_message",
            ]
        )

        try:

            raise self.retry(
                exc=exc,
                countdown=60,
            )

        except self.MaxRetriesExceededError:

            return {
                "status": "failed",
                "webhook_id": webhook_id,
                "error": str(exc),
            }


def process_ticket_created(payload):

    print(
        "Processing ticket.created:",
        payload,
    )


def process_ticket_updated(payload):

    print(
        "Processing ticket.updated:",
        payload,
    )


def process_ticket_closed(payload):

    print(
        "Processing ticket.closed:",
        payload,
    )


@shared_task
def send_notification(
    user_id,
    subject,
    message,
):

    # Replace this with your email/notification service.

    print(
        f"Sending notification to user {user_id}"
    )

    print(
        f"Subject: {subject}"
    )

    print(
        f"Message: {message}"
    )

    return True