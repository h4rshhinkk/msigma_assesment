from django.urls import path
from .views import HealthAPI

urlpatterns = [
    path("", HealthAPI.as_view({"get": "listing"})),
]