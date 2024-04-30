from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import CharField
from django.db.models.aggregates import Sum
from django.utils import timezone
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


class Manager(User):
    class Meta:
        verbose_name = _("Manager")
        verbose_name_plural = _("Managers")


class CashCollector(User):
    freeze_time = models.DateTimeField(null=True, blank=True)

    @property
    def pocket_value(self):
        return self.pocket_values.filter(transfer__isnull=True).aggregate(total=Sum('amount'))['total'] or 0

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pocket_value > settings.FREEZING_AMOUNT_THRESHOLD:
            self.freeze_time = timezone.now() + timedelta(days=settings.FREEZING_DAYS_THRESHOLD)
            super().save(*args, update_fields=['freeze_time'], **kwargs)

    class Meta:
        verbose_name = _("Cash Collector")
        verbose_name_plural = _("Cash Collectors")
