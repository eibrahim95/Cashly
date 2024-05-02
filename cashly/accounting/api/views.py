from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from cashly.accounting.api.serializers import CashCollectorPocketSerializer
from cashly.accounting.api.serializers import CentralSafeSerializer
from cashly.accounting.api.serializers import TimeLineSerializer
from cashly.accounting.models import CashCollectorPocket
from cashly.accounting.models import CashCollectorTimeLine
from cashly.billing.models import CustomerBill
from cashly.users.models import CashCollector


class CollectBillView(APIView):
    def post(self, request, **kwargs):
        next_bill = (
            CustomerBill.objects.filter(
                collector=CashCollector.objects.get(pk=self.request.user.pk),
                collected_pocket__isnull=True,
            )
            .order_by("due_date")
            .first()
        )
        if next_bill:
            serializer = CashCollectorPocketSerializer(
                data={"bill": next_bill.pk},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Nothing to collect."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PocketView(ListAPIView):
    serializer_class = CashCollectorPocketSerializer
    queryset = CashCollectorPocket.objects.all()

    def get_queryset(self):
        return CashCollectorPocket.objects.filter(
            collector=CashCollector.objects.get(pk=self.request.user.pk),
            transfer__isnull=True,
        )


class PayView(CreateAPIView):
    serializer_class = CentralSafeSerializer


class CashCollectorStatusReportView(ListAPIView):
    serializer_class = TimeLineSerializer
    queryset = CashCollectorTimeLine.objects.all()

    def get_queryset(self):
        return CashCollectorTimeLine.objects.filter(
            collector=CashCollector.objects.get(pk=self.request.user.pk),
        )
