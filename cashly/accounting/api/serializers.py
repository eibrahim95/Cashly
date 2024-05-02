from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

from cashly.accounting.models import CashCollectorPocket
from cashly.accounting.models import CashCollectorTimeLine
from cashly.accounting.models import CentralSafe
from cashly.users.models import CashCollector


class CashCollectorPocketSerializer(serializers.ModelSerializer):
    payed_at = serializers.SerializerMethodField(required=False)
    amount = serializers.SerializerMethodField()

    class Meta:
        model = CashCollectorPocket
        fields = ("id", "amount", "collected_at", "payed_at", "bill")
        read_only_fields = ("collector", "collected_at")
        extra_kwargs = {
            "bill": {"write_only": True},
        }

    def get_amount(self, obj):
        return obj.bill.amount

    def get_payed_at(self, obj):
        return obj.transfer.transferred_at if hasattr(obj, "transfer") else None

    def create(self, validated_data):
        try:
            obj = CashCollectorPocket.objects.create(
                **validated_data,
                collected_at=timezone.now(),
                collector=CashCollector.objects.get(pk=self.context["request"].user.pk),
            )
        except ValidationError as e:
            raise serializers.ValidationError(
                {"non_field_errors": e.messages},
            ) from e
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError({"bill": ["Bill does not exist"]}) from e
        return obj


class CentralSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentralSafe
        fields = ("id", "pocket", "transferred_at")
        read_only_fields = ("transferred_at",)

    def create(self, validated_data):
        return CentralSafe.objects.create(
            **validated_data,
            transferred_at=timezone.now(),
        )


class TimeLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashCollectorTimeLine
        fields = ("pocket_value", "transaction_value", "checkpoint_time", "frozen")
