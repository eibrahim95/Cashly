from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from cashly.users.models import CashCollector
from cashly.users.models import Manager


class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


class ManagerAuthentication(BearerTokenAuthentication):
    def authenticate(self, request):
        user, token = super().authenticate(request)
        if user and token:
            if not Manager.objects.filter(pk=user.pk).exists():
                msg = _("Invalid token header. No credentials provided.")
                raise exceptions.AuthenticationFailed(msg)
        return user, token


class CashCollectorAuthentication(BearerTokenAuthentication):
    def authenticate(self, request):
        user, token = super().authenticate(request)
        if user and token:
            if not CashCollector.objects.filter(pk=user.pk).exists():
                msg = _("Invalid token header. No credentials provided.")
                raise exceptions.AuthenticationFailed(msg)
        return user, token
