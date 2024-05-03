import pytest

from cashly.users.models import CashCollector
from cashly.users.models import Manager
from cashly.users.models import User
from cashly.users.tests.factories import CashCollectorFactory
from cashly.users.tests.factories import ManagerFactory
from cashly.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture()
def user(db) -> User:
    return UserFactory()


@pytest.fixture()
def collector(db) -> CashCollector:
    return CashCollectorFactory()


@pytest.fixture()
def manager(db) -> Manager:
    return ManagerFactory()
