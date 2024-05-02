from django.urls import path

from cashly.accounting.api.views import CashCollectorStatusReportView
from cashly.accounting.api.views import CollectBillView
from cashly.accounting.api.views import PayView
from cashly.accounting.api.views import PocketView

urlpatterns = [
    path("api/v1/collect/", CollectBillView.as_view()),
    path("api/v1/pocket/", PocketView.as_view()),
    path("api/v1/pay/", PayView.as_view()),
    path("api/v1/collector-status-report/", CashCollectorStatusReportView.as_view()),
]
