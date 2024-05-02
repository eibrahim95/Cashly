from django.utils import timezone
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from cashly.users.models import CashCollector

from .serializers import CashCollectorSerializer


class CashCollectorViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = CashCollectorSerializer
    queryset = CashCollector.objects.all()
    lookup_field = "username"

    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)


class CashCollectorStatus(APIView):
    def get(self, request, **kwargs):
        collector = CashCollector.objects.get(pk=request.user.pk)
        return Response({"is_frozen": timezone.now() >= collector.freeze_time})
