from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from cashly.billing.api.serializers import CustomerBillSerializer
from cashly.billing.api.serializers import CustomerSerializer
from cashly.billing.models import Customer
from cashly.billing.models import CustomerBill
from cashly.users.authentication import CashCollectorAuthentication
from cashly.users.authentication import ManagerAuthentication
from cashly.users.models import CashCollector
from cashly.users.models import Manager


class CustomerViewSet(
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    authentication_classes = (ManagerAuthentication,)

    def destroy(self, *args, **kwargs):
        try:
            super().destroy(*args, **kwargs)
            return Response({"detail": "ok"}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(
                {
                    "non_field_errors": [
                        "Cannot delete because there are related items depending "
                        "on this item, please delete those items first",
                    ],
                },
            )


class CustomerBillViewSet(
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = CustomerBillSerializer
    queryset = CustomerBill.objects.all()
    authentication_classes = (ManagerAuthentication,)

    def get_queryset(self):
        return CustomerBill.objects.filter(
            creator=Manager.objects.get(pk=self.request.user.pk),
        )

    def destroy(self, *args, **kwargs):
        try:
            super().destroy(*args, **kwargs)
            return Response({"detail": "ok"}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(
                {
                    "non_field_errors": [
                        "Cannot delete because there are related items depending "
                        "on this item, please delete those items first",
                    ],
                },
            )


class CollectedBills(ListAPIView):
    serializer_class = CustomerBillSerializer
    queryset = CustomerBill.objects.all()
    authentication_classes = (CashCollectorAuthentication,)

    def get_queryset(self):
        return CustomerBill.objects.filter(
            collector=CashCollector.objects.get(pk=self.request.user.pk),
            collected_pocket__isnull=False,
        )


class NextDueBill(APIView):
    authentication_classes = (CashCollectorAuthentication,)

    def get(self, request, **kwargs):
        next_bill = (
            CustomerBill.objects.filter(
                collector=CashCollector.objects.get(pk=self.request.user.pk),
                collected_pocket__isnull=True,
            )
            .order_by("due_date")
            .first()
        )
        if next_bill:
            return Response(CustomerBillSerializer(next_bill).data)
        return Response({})
