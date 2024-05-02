from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models import Sum
from django.db.models import Window
from django.utils import timezone
from django.utils.timezone import localtime

from cashly.billing.models import CustomerBill
from cashly.users.models import CashCollector


class CashCollectorPocket(models.Model):
    collector = models.ForeignKey(
        CashCollector,
        on_delete=models.PROTECT,
        related_name="pocket_values",
    )
    bill = models.OneToOneField(
        CustomerBill,
        on_delete=models.PROTECT,
        related_name="collected_pocket",
    )
    collected_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pk} - {self.bill.amount}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.collected_at >= self.collector.freeze_time:
                error_message = "This collector is frozen and cannot collect any bills."
                raise ValidationError(
                    error_message,
                )
        if self.bill.collector != self.collector:
            error_message = "This collector doesn't have access to this bill."
            raise ValidationError(
                error_message,
            )
        super().save(*args, **kwargs)
        self.update_freezing_status()

    def update_freezing_status(self):
        if self.collector.pocket_value > settings.FREEZING_AMOUNT_THRESHOLD:
            last_collected = (
                CashCollectorPocket.objects.filter(
                    transfer__isnull=True,
                    collector=self.collector,
                )
                .order_by("collected_at")
                .annotate(
                    total=Window(
                        expression=Sum("bill__amount"),
                        order_by=F("collected_at").asc(),
                    ),
                )
                .values("collected_at", "total")
            )
            for collection in last_collected:
                if collection.get("total") > settings.FREEZING_AMOUNT_THRESHOLD:
                    self.collector.freeze_time = localtime(
                        collection.get("collected_at"),
                    ) + timedelta(days=settings.FREEZING_DAYS_THRESHOLD)
                    self.collector.save()
                    break
        else:
            self.collector.freeze_time = None
            self.collector.save()


class CentralSafe(models.Model):
    pocket = models.OneToOneField(
        CashCollectorPocket,
        on_delete=models.PROTECT,
        related_name="transfer",
    )
    transferred_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pk} - {self.pocket.bill.amount}: {self.transferred_at}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.pocket.update_freezing_status()
