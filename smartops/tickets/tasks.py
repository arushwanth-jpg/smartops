from celery import shared_task  
from django.utils import timezone
from tickets.models import Ticket


@shared_task
def check_sla_check():
    now = timezone.now()
    tickets = Ticket.objects.exclude(
        status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED],
    ).exclude(sla_due_at=None)
    near_breach_count = 0
    breached_count = 0
    for ticket in tickets:
        if ticket.sla_due_at <= now:
            breached_count += 1
            
            print(f"Ticket {ticket.id} has breached SLA.")
        else:
            remaining =(ticket.sla_due_at - now)
            remaining_hours = remaining.total_seconds() / 3600
            if remaining_hours <= 1:
                near_breach_count += 1
                print(f"Ticket {ticket.id} is near SLA breach. Remaining time: {remaining_hours:.2f} hours.")   
                
    return {
        "near_breach_count": near_breach_count,
        "breached_count": breached_count,
    }