from rest_framework.routers import DefaultRouter
from .views import WebhookEndpointViewSet, WebhookDeliveryViewSet

router = DefaultRouter()
router.register(r'webhook-endpoints', WebhookEndpointViewSet)
router.register(r'webhook-deliveries', WebhookDeliveryViewSet)

urlpatterns = router.urls