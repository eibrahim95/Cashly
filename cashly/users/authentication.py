import abc

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from cashly.users.models import CashCollector
from cashly.users.models import Manager


class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class RoleBasedAuthentication(BearerTokenAuthentication, abc.ABC):
    role_model = None

    def authenticate(self, request):
        if not self.role_model:
            raise NotImplementedError
        try:
            user, token = super().authenticate(request)
        except TypeError:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg) from TypeError
        if user and token:
            if not self.role_model.objects.filter(pk=user.pk).exists():
                msg = _("Invalid token header. No credentials provided.")
                raise exceptions.AuthenticationFailed(msg)
        return user, token


class ManagerAuthentication(RoleBasedAuthentication):
    role_model = Manager


class CashCollectorAuthentication(RoleBasedAuthentication):
    role_model = CashCollector
