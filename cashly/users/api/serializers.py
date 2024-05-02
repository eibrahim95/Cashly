from rest_framework import serializers

from cashly.users.models import CashCollector
from cashly.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class CashCollectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashCollector
        fields = ("pk", "username", "name")
        write_only_fields = ("password",)
