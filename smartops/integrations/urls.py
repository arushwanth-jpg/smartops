from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    IntegrationLogViewSet,
    WebhookEventViewSet,
    webhook_receiver,
)


router = DefaultRouter()

router.register(
    "webhooks",
    WebhookEventViewSet,
    basename="webhook-event",
)

router.register(
    "logs",
    IntegrationLogViewSet,
    basename="integration-log",
)


urlpatterns = [

    path(
        "webhook/",
        webhook_receiver,
        name="webhook-receiver",
    ),

]

urlpatterns += router.urls