from django.urls import path

from cashly.billing.api.views import CollectedBills
from cashly.billing.api.views import NextDueBill

urlpatterns = [
    path("api/v1/tasks/", CollectedBills.as_view(), name="tasks"),
    path("api/v1/next_task/", NextDueBill.as_view(), name="next_task"),
]
