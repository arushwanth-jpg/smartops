from django.shortcuts import render
from rest_framework import viewsets
from .models import webhookendpoint, webhookdelivery
from .serializers import WebhookEndpointSerializer, WebhookDeliverySerializer
from .permissions import IsAdmin

class WebhookEndpointViewSet(viewsets.ModelViewSet):
    queryset = webhookendpoint.objects.select_related().order_by('-created_at')
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAdmin]
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = webhookdelivery.objects.select_related('endpoint').all().order_by('-created_at')
    serializer_class = WebhookDeliverySerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['status', 'endpoint', 'event_type']
    
