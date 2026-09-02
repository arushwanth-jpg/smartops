from django.contrib import admin
from .models import webhookendpoint, webhookdelivery

@admin.register(webhookendpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "is_active", "created_by", "created_at", "updated_at")
    search_fields = ("name", "url")
    list_filter = ("is_active", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    
@admin.register(webhookdelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "event_type", "status", "response_status", "delivered_at", "attempt_count", "created_at")
    search_fields = ("endpoint__name", "event_type")
    list_filter = ("status", "delivered_at", "created_at")
    readonly_fields = ("created_at", "delivered_at")
    


