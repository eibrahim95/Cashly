from django.db import models

from cashly.billing.models import CustomerBill
from cashly.users.models import CashCollector


class CashCollectorPocket(models.Model):
    collector = models.ForeignKey(CashCollector, on_delete=models.PROTECT, related_name='pocket_values')
    bill = models.OneToOneField(CustomerBill, on_delete=models.PROTECT, related_name='collected_pocket')
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    collected_at = models.DateTimeField(null=True, blank=True)


class CentralSafe(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    pocket = models.OneToOneField(CashCollectorPocket, on_delete=models.PROTECT, related_name='transfer')
    transferred_at = models.DateTimeField(null=True, blank=True)
