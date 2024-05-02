from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView

from cashly.accounting.api.serializers import CashCollectorPocketSerializer
from cashly.accounting.api.serializers import CentraSafeSerializer
from cashly.accounting.models import CashCollectorPocket
from cashly.users.models import CashCollector


class CollectBillView(CreateAPIView):
    serializer_class = CashCollectorPocketSerializer


class PocketView(ListAPIView):
    serializer_class = CashCollectorPocketSerializer
    queryset = CashCollectorPocket.objects.all()

    def get_queryset(self):
        return CashCollectorPocket.objects.filter(
            collector=CashCollector.objects.get(pk=self.request.user.pk),
            transfer__isnull=True,
        )


class PayView(CreateAPIView):
    serializer_class = CentraSafeSerializer
