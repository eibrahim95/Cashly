from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from cashly.accounting.models import CashCollectorPocket
from cashly.accounting.models import CentralSafe
from cashly.billing.models import Customer
from cashly.billing.models import CustomerBill
from cashly.users.tests.factories import CashCollectorFactory
from cashly.users.tests.factories import ManagerFactory


class CustomerFactory(DjangoModelFactory):
    name = Faker("name")
    address = Faker("address")

    class Meta:
        model = Customer


class CustomerBillFactory(DjangoModelFactory):
    customer = SubFactory(CustomerFactory)
    creator = SubFactory(ManagerFactory)
    collector = SubFactory(CashCollectorFactory)
    amount = Faker("pydecimal", left_digits=3, right_digits=4)
    due_date = Faker("date")

    class Meta:
        model = CustomerBill


class CashCollectorPocketFactory(DjangoModelFactory):
    collector = SubFactory(CashCollectorFactory)
    bill = SubFactory(CustomerBillFactory)
    collected_at = Faker("date_time")

    class Meta:
        model = CashCollectorPocket


class CentralSafaFactory(DjangoModelFactory):
    pocket = SubFactory(CashCollectorPocketFactory)
    address = Faker("address")

    class Meta:
        model = CentralSafe
