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
        fields = ("pk", "username", "name", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Set the password
        user.save()
        return user

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)  # Set the new password
        return super().update(instance, validated_data)
