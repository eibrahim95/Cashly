import pytest
from rest_framework.test import APIRequestFactory

from cashly.users.api.views import CashCollectorViewSet
from cashly.users.models import CashCollector


class TestCashCollectorViewSet:
    @pytest.fixture()
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, collector: CashCollector, api_rf: APIRequestFactory):
        view = CashCollectorViewSet()
        request = api_rf.get("/fake-url/")
        request.user = collector

        view.request = request

        assert collector in view.get_queryset()
