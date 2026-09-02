from .models import webhookendpoint
from .tasks import send_webhook

def trigger_webhook(event_type, payload):   
    endpoints = webhookendpoint.objects.filter(is_active=True)
    for endpoint in endpoints:  
        send_webhook.delay(event_type, payload, endpoint.id)