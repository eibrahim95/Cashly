from django.db import models

from cashly.users.models import CashCollector
from cashly.users.models import Manager


class Customer(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)

    class Meta:
        verbose_name_plural = " Customers"

    def __str__(self):
        return self.name


class CustomerBill(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="bills",
    )
    creator = models.ForeignKey(
        Manager,
        on_delete=models.PROTECT,
        related_name="created_bills",
    )
    collector = models.ForeignKey(
        CashCollector,
        on_delete=models.PROTECT,
        related_name="assigned_bills",
    )
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.pk} - {self.creator}: {self.amount}"
