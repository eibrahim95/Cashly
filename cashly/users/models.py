from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.db.models.aggregates import Sum
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Cashly.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def __str__(self):
        return f"{self.username}"


class Manager(User):
    class Meta:
        verbose_name = _(" Manager")
        verbose_name_plural = _(" Managers")


class CashCollector(User):
    freeze_time = models.DateTimeField(null=True, blank=True)

    @property
    def pocket_value(self):
        return (
            self.pocket_values.filter(transfer__isnull=True).aggregate(
                total=Sum("bill__amount"),
            )["total"]
            or 0
        )

    class Meta:
        verbose_name = _("Cash Collector")
        verbose_name_plural = _("Cash Collectors")
