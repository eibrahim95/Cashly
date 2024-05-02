from django.urls import path

from .api.views import CashCollectorStatus

app_name = "users"
urlpatterns = [
    path("api/v1/status/", CashCollectorStatus.as_view()),
]
