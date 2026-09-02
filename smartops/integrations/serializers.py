from rest_framework import serializers
from .models import webhookendpoint, webhookdelivery



class WebhookEndpointSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = webhookendpoint
        fields = ['id', 'name', 'url', 'created_by', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
        
class WebhookDeliverySerializer(serializers.ModelSerializer):
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)
    
    class Meta:
        model = webhookdelivery
        fields = ['id', 'endpoint', 'endpoint_name', 'event_type', 'payload', 'status', 'response_status', 'response_body', 'delivered_at', 'attempt_count', 'created_at']
        read_only_fields = ['id', 'endpoint_name', 'status', 'response_status', 'response_body', 'delivered_at', 'attempt_count', 'created_at']