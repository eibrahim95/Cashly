from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import localtime
from freezegun import freeze_time
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from cashly.accounting.tests.factories import CustomerBillFactory


class TestEdgeCases:
    @pytest.fixture()
    def api_client(self) -> APIClient:
        return APIClient()

    def test_nothing_to_collect(self, api_client: APIClient, collector) -> None:
        collector_token = Token.objects.create(user=collector)
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + collector_token.key)

        response = api_client.post(reverse("collect-bill"), {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db()
    def test_collecting_exactly_at_freeze_time(self, api_client: APIClient):
        bill = CustomerBillFactory(amount=settings.FREEZING_AMOUNT_THRESHOLD + 1)
        collector_token = Token.objects.create(user=bill.collector)
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + collector_token.key)
        response = api_client.post(reverse("collect-bill"), {})
        assert response.status_code == status.HTTP_200_OK

        bill.collector.refresh_from_db()
        CustomerBillFactory(amount=1, collector=bill.collector)
        freezing_time = bill.collector.freeze_time
        with freeze_time(
            localtime(freezing_time),
        ):  # Freeze the time for the duration of this block
            response = api_client.post(reverse("collect-bill"), {})
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {
                "non_field_errors": [
                    "This collector is frozen and cannot collect any bills.",
                ],
            }

    def test_collector_non_freezing_in_the_days_threshold(
        self,
        api_client: APIClient,
        collector,
    ) -> None:
        bill = CustomerBillFactory(amount=settings.FREEZING_AMOUNT_THRESHOLD + 1)
        collector_token = Token.objects.create(user=bill.collector)
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + collector_token.key)
        response = api_client.post(reverse("collect-bill"), {})
        assert response.status_code == status.HTTP_200_OK
        pocket_pk = response.json().get("id")
        bill.collector.refresh_from_db()
        CustomerBillFactory(amount=1, collector=bill.collector)
        freezing_time = bill.collector.freeze_time
        with freeze_time(
            localtime(freezing_time) - timedelta(seconds=1),
        ):
            response = api_client.post(reverse("pay-pocket"), {"pocket": pocket_pk})
            assert response.status_code == status.HTTP_201_CREATED
        with freeze_time(
            localtime(freezing_time),
        ):
            response = api_client.post(reverse("collect-bill"), {})
            assert response.status_code == status.HTTP_200_OK
