from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

try:
    from rest_framework.authtoken.models import TokenProxy as DRFToken
except ImportError:
    from rest_framework.authtoken.models import Token as DRFToken

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import CashCollector
from .models import Manager
from .models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    search_fields = ["name"]


@admin.register(Manager)
class ManagerAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(CashCollector)
class CashControllerAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Important dates"),
            {"fields": ("freeze_time", "last_login", "date_joined")},
        ),
    )
    list_display = ["username", "name", "pocket_value", "freeze_time"]

    def pocket_value(self, obj):
        return obj.pocket_value


admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(DRFToken)
