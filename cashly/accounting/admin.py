from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from cashly.accounting.models import CashCollectorPocket
from cashly.accounting.models import CashCollectorTimeLine
from cashly.accounting.models import CentralSafe
from cashly.billing.models import CustomerBill


class CashCollectorPocketAdminForm(forms.ModelForm):
    class Meta:
        model = CashCollectorPocket
        fields = ("collector", "bill", "collected_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Don't show already created bills.
            self.fields["bill"].queryset = CustomerBill.objects.filter(
                collected_pocket__isnull=True,
            )


class Transfer(admin.StackedInline):
    model = CentralSafe
    readonly_fields = ("transferred_at",)
    extra = 0


@admin.register(CashCollectorPocket)
class CashCollectorPocketAdmin(admin.ModelAdmin):
    list_display = ("id", "collector", "amount", "collected_at", "payed")
    readonly_fields_on_change = ("bill",)
    form = CashCollectorPocketAdminForm
    ordering = ("collected_at",)
    search_fields = ("collector__username",)

    def amount(self, obj):
        return obj.bill.amount

    def payed(self, obj):
        return "YES" if hasattr(obj, "transfer") else "NO"

    def get_inlines(self, request, obj=None):
        if obj and hasattr(
            obj,
            "transfer",
        ):  # Show inline only when editing existing instance
            return (Transfer,)
        return ()

    def get_readonly_fields(self, request, obj=None):
        # If obj is None, it means we are in the add view
        if obj is None:
            # For add view, return an empty tuple to make no fields read-only
            return ()
        # For change view, return the readonly fields defined for change
        if hasattr(obj, "transfer") is not None:
            return (
                "collector",
                "bill",
            )
        return self.readonly_fields_on_change

    def message_user(
        self,
        *args,
        **kwargs,
    ):
        if not hasattr(self, "stop_messages"):
            super().message_user(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        try:
            obj.save()  # Save the object
        except ValidationError as e:
            self.message_user(request, "\n".join(e.messages), level="ERROR")
            self.stop_messages = True
            return
        else:
            super().save_model(request, obj, form, change)


class CentralSafeAdminForm(forms.ModelForm):
    class Meta:
        model = CentralSafe
        fields = ("pocket", "transferred_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Don't show already transferred pockets
            self.fields["pocket"].queryset = CashCollectorPocket.objects.filter(
                transfer__isnull=True,
            )


@admin.register(CentralSafe)
class CentralSafe(admin.ModelAdmin):
    list_display = ("id", "transferred_at", "collector", "manager")
    form = CentralSafeAdminForm

    def collector(self, obj):
        return obj.pocket.collector

    def manager(self, obj):
        return obj.pocket.bill.creator


@admin.register(CashCollectorTimeLine)
class CashCollectorTimeLine(admin.ModelAdmin):
    list_display = (
        "collector",
        "pocket_value",
        "transaction_value",
        "checkpoint_time",
        "frozen",
    )
    search_fields = ("collector",)
    ordering = ("checkpoint_time",)
