from django.contrib import admin

from cashly.accounting.models import CashCollectorPocket

from .models import Customer
from .models import CustomerBill


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin): ...


class CustomerBillCollection(admin.StackedInline):
    model = CashCollectorPocket
    readonly_fields = ("collector", "bill", "collected_at")
    extra = 0


@admin.register(CustomerBill)
class CustomerBillAdmin(admin.ModelAdmin):
    list_display = ("pk", "creator", "collector", "amount", "due_date")
    inlines = (CustomerBillCollection,)
    readonly_fields_on_change = ("creator",)

    def get_inlines(self, request, obj=None):
        if obj and hasattr(
            obj,
            "collected_pocket",
        ):  # Show inline only when editing existing instance
            return (CustomerBillCollection,)
        return ()

    def get_readonly_fields(self, request, obj=None):
        # If obj is None, it means we are in the add view
        if obj is None:
            # For add view, return an empty tuple to make no fields read-only
            return ()
        # For change view, return the readonly fields defined for change
        if hasattr(obj, "collected_pocket"):
            return ("creator", "collector", "amount", "customer", "due_date")
        return self.readonly_fields_on_change
