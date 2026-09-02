import hashlib
import hmac
import json
from django.conf import settings
from django.utils import timezone
import requests
from .models import webhookdelivery,webhookendpoint
from celery import shared_task

@shared_task(bind=True,auto_retry_for=(requests.RequestException), retry_backoff=True, retry_kwargs={'max_retries': 5})
def send_webhook(self,event_type, payload, endpoint_id):
    endpoint = webhookendpoint.objects.get(id=endpoint_id, is_active=True)
    delivery = webhookdelivery.objects.create(endpoint=endpoint, event_type=event_type, payload=payload)
    payload_json = json.dumps(payload, separators=(',', ':'),sort_keys=True)
    signature = hmac.new(settings.WEBHOOK_SECRET.encode(), payload_json.encode(), hashlib.sha256).hexdigest()
    headers = {'Content-Type': 'application/json',
               'X-smartops-signature': signature,
               'X-smartops-Event': event_type}
    
    try:
        delivery.attempt_count += 1
        response = requests.post(
            endpoint.url,
            data=payload_json,
            headers=headers,
            timeout=10,
        )

        delivery.response_status = (
            response.status_code
        )

        delivery.response_body = (
            response.text[:2000]
        )

        response.raise_for_status()

        delivery.status = (
            webhookdelivery.Status.SUCCESS
        )

        delivery.delivered_at = (
            timezone.now()
        )

        delivery.save()

        return {
            "status": "success",
            "delivery_id": delivery.id,
        }

    except requests.RequestException:

        delivery.status = (
            webhookdelivery.Status.FAILED
        )

        delivery.save()

        raise
        
    