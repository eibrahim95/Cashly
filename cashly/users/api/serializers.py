from rest_framework import serializers

from cashly.users.models import CashCollector


class CashCollectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashCollector
        fields = ("pk", "username", "name", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    @staticmethod
    def create(validated_data):
        password = validated_data.pop("password")
        user = CashCollector.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)
        return super().update(instance, validated_data)
