from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from cashly.billing.api.views import CustomerBillViewSet
from cashly.billing.api.views import CustomerViewSet
from cashly.users.api.views import CashCollectorViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("collectors", CashCollectorViewSet)
router.register("customers", CustomerViewSet)
router.register("bills", CustomerBillViewSet)


app_name = "api"
urlpatterns = router.urls
