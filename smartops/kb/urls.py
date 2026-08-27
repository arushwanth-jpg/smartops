from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    KBArticleViewSet,
    TicketKBLinkViewSet,
)


router = DefaultRouter()

router.register(
    r"articles",
    KBArticleViewSet,
    basename="kb-articles",
)

router.register(
    r"links",
    TicketKBLinkViewSet,
    basename="kb-links",
)


urlpatterns = router.urls