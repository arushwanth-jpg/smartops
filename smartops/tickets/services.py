from datetime import timedelta

from django.utils import timezone


SLA_HOURS = {
    "LOW": 72,
    "MEDIUM": 48,
    "HIGH": 24,
    "CRITICAL": 4,
}


def calculate_sla_due_at(priority):

    hours = SLA_HOURS.get(
        priority,
        48,
    )

    return timezone.now() + timedelta(
        hours=hours
    )