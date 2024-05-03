from datetime import datetime
from datetime import timedelta

import pytest
from dateutil import parser
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from cashly.accounting.models import CashCollectorTimeLine
from cashly.accounting.tests.factories import CashCollectorPocketFactory
from cashly.accounting.tests.factories import CustomerBillFactory
from cashly.accounting.tests.factories import CustomerFactory
from cashly.users.models import CashCollector
from cashly.users.models import Manager

MAIN_SCENARIO = [
    {"amount": 1000, "time": "2000-01-01 06:00"},
    {"amount": 6000, "time": "2000-01-01 07:00"},
    {"amount": 2000, "time": "2000-01-02 08:00"},
]
EXPECTED_NUMBER_OF_HISTORY = 4


def parse_time(time_as_str):
    return timezone.make_aware(
        datetime.strptime(time_as_str, "%Y-%m-%d %H:%M"),  # noqa: DTZ007
        timezone.get_current_timezone(),
    )


# Make sure we set the settings that align with our assumption in the test
@override_settings(FREEZING_DAYS_THRESHOLD=2, FREEZING_AMOUNT_THRESHOLD=5000)
def test_main_scenario(manager: Manager, collector: CashCollector):
    customer = CustomerFactory()

    for collection in MAIN_SCENARIO:
        bill = CustomerBillFactory.create(
            amount=collection["amount"],
            customer=customer,
            creator=manager,
            collector=collector,
        )
        CashCollectorPocketFactory.create(
            bill=bill,
            collector=collector,
            collected_at=parse_time(collection["time"]),
        )
    history = (
        CashCollectorTimeLine.objects.filter(collector=collector)
        .order_by("checkpoint_time")
        .all()
    )

    assert len(history) == EXPECTED_NUMBER_OF_HISTORY
    for i in range(3):
        assert history[i].checkpoint_time == parse_time(MAIN_SCENARIO[i]["time"])
        assert history[i].transaction_value == MAIN_SCENARIO[i]["amount"]
        assert history[i].frozen is False

    assert history[3].frozen is True
    assert history[3].checkpoint_time == parse_time(
        MAIN_SCENARIO[1]["time"],
    ) + timedelta(days=settings.FREEZING_DAYS_THRESHOLD)


class TestMainScenario:
    @pytest.fixture()
    def api_client(self) -> APIClient:
        return APIClient()

    @override_settings(FREEZING_DAYS_THRESHOLD=2, FREEZING_AMOUNT_THRESHOLD=5000)
    def test_main_scenario(
        self,
        manager: Manager,
        collector: CashCollector,
        api_client,
    ):
        manager_token = Token.objects.create(user=manager)
        collector_token = Token.objects.create(user=collector)
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + manager_token.key)

        customer = CustomerFactory.build()
        response = api_client.post(
            reverse("api:customer-list"),
            {"name": customer.name, "address": customer.address},
        )
        assert response.status_code == status.HTTP_201_CREATED
        customer_pk = response.json().get("id")

        for collection in MAIN_SCENARIO:
            response = api_client.post(
                reverse("api:customerbill-list"),
                {
                    "amount": collection["amount"],
                    "customer": customer_pk,
                    "collector": collector.pk,
                    "due_date": timezone.now().date(),
                },
            )
            assert response.status_code == status.HTTP_201_CREATED

        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + collector_token.key)
        for i in range(len(MAIN_SCENARIO)):
            with freeze_time(
                parse_time(MAIN_SCENARIO[i]["time"]),
            ):  # Freeze the time for the duration of this block
                response = api_client.post(reverse("collect-bill"), {})
                assert response.status_code == status.HTTP_200_OK
        response = api_client.get(reverse("status-report"), {})
        assert response.status_code == status.HTTP_200_OK
        history = response.json().get("results")

        assert len(history) == EXPECTED_NUMBER_OF_HISTORY
        for i in range(3):
            assert parser.parse(history[i].get("checkpoint_time")) == parse_time(
                MAIN_SCENARIO[i]["time"],
            )
            assert (
                history[i].get("transaction_value")
                == f'{MAIN_SCENARIO[i]["amount"]:.4f}'
            )
            assert history[i].get("frozen") is False

        assert history[3].get("frozen") is True
        assert parser.parse(history[3].get("checkpoint_time")) == parse_time(
            MAIN_SCENARIO[1]["time"],
        ) + timedelta(days=settings.FREEZING_DAYS_THRESHOLD)
