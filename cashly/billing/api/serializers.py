from rest_framework import serializers

from cashly.billing.models import Customer
from cashly.billing.models import CustomerBill
from cashly.users.models import Manager


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "name", "address")


class CustomerBillSerializer(serializers.ModelSerializer):
    collected_at = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomerBill
        fields = (
            "id",
            "customer",
            "creator",
            "collector",
            "amount",
            "due_date",
            "collected_at",
        )
        read_only_fields = ("creator", "collected_at")

    def get_collected_at(self, obj):
        return (
            obj.collected_pocket.collected_at
            if hasattr(obj, "collected_pocket")
            else None
        )

    def create(self, validated_data):
        return CustomerBill.objects.create(
            **validated_data,
            creator=Manager.objects.get(pk=self.context["request"].user.pk),
        )
