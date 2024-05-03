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


class CashCollectorTimeLine(models.Model):
    collector = models.ForeignKey(
        CashCollector,
        on_delete=models.PROTECT,
        related_name="timeline",
    )
    pocket_value = models.DecimalField(max_digits=40, decimal_places=4)
    transaction_value = models.DecimalField(max_digits=40, decimal_places=4)
    checkpoint_time = models.DateTimeField(default=timezone.now)
    amount_threshold_then = models.IntegerField()
    days_threshold_then = models.IntegerField()
    frozen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.checkpoint_time}"


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

    class Meta:
        verbose_name = "  Cash Collector Pocket"
        verbose_name_plural = "  Cash Collector Pocket"

    def __str__(self):
        return f"{self.pk} - {self.bill.amount}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        just_froze = self.update_freezing_status()
        self.create_checkpoint(self.collected_at, self.bill.amount)
        self.sync_freezing_checkpoint(just_froze)

    def clean(self):
        if self.pk is None and (
            self.collector.freeze_time
            and self.collected_at >= self.collector.freeze_time
        ):
            error_message = "This collector is frozen and cannot collect any bills."
            raise ValidationError(
                error_message,
            )
        if self.bill.collector != self.collector:
            error_message = "This collector doesn't have access to this bill."
            raise ValidationError(
                error_message,
            )

    def create_checkpoint(self, checkpoint_time, transaction_value):
        frozen = (
            self.collector.freeze_time
            and self.collector.freeze_time <= self.collected_at
            or False
        )
        CashCollectorTimeLine.objects.create(
            collector=self.collector,
            pocket_value=self.collector.pocket_value if not frozen else -1,
            transaction_value=transaction_value,
            checkpoint_time=checkpoint_time,
            amount_threshold_then=settings.FREEZING_AMOUNT_THRESHOLD,
            days_threshold_then=settings.FREEZING_DAYS_THRESHOLD,
            frozen=frozen,
        )

    def update_freezing_status(self):
        if self.collector.pocket_value > settings.FREEZING_AMOUNT_THRESHOLD:
            if self.collector.freeze_time is None:
                self.collector.freeze_time = self.get_freeze_time()
                self.collector.save()
                return True
        else:
            self.collector.freeze_time = None
            self.collector.save()
        return False

    def get_freeze_time(self):
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
                return localtime(
                    collection.get("collected_at"),
                ) + timedelta(days=settings.FREEZING_DAYS_THRESHOLD)
        return None

    def sync_freezing_checkpoint(self, just_froze):
        if just_froze:
            CashCollectorTimeLine.objects.get_or_create(
                collector=self.collector,
                checkpoint_time=self.collector.freeze_time,
                defaults={
                    "pocket_value": -1,
                    "transaction_value": 0,
                    "days_threshold_then": settings.FREEZING_DAYS_THRESHOLD,
                    "amount_threshold_then": settings.FREEZING_AMOUNT_THRESHOLD,
                    "frozen": True,
                },
            )
        if not self.collector.freeze_time:
            last_collected_value = (
                CashCollectorPocket.objects.filter(
                    collector=self.collector,
                )
                .order_by("collected_at")
                .last()
            )
            if last_collected_value:
                CashCollectorTimeLine.objects.filter(
                    collector=self.collector,
                    checkpoint_time__gt=localtime(last_collected_value.collected_at),
                    pocket_value=-1,
                ).all().delete()


class CentralSafe(models.Model):
    pocket = models.OneToOneField(
        CashCollectorPocket,
        on_delete=models.PROTECT,
        related_name="transfer",
    )
    transferred_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = " Central Safe"
        verbose_name_plural = " Central Safe"

    def __str__(self):
        return f"{self.pk} - {self.pocket.bill.amount}: {self.transferred_at}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        just_froze = self.pocket.update_freezing_status()
        self.pocket.create_checkpoint(self.transferred_at, self.pocket.bill.amount * -1)
        self.pocket.sync_freezing_checkpoint(just_froze)
