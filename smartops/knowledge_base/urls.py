from rest_framework.routers import DefaultRouter

from .views import (
    KBArticleViewSet,
    TicketKBLinkViewSet,
)

router = DefaultRouter()

router.register(
    "articles",
    KBArticleViewSet,
    basename="kb-article",
)

router.register(
    "ticket-links",
    TicketKBLinkViewSet,
    basename="ticket-kb-link",
)

urlpatterns = router.urls