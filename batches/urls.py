from django.urls import path
from .views import BatchAPI

urlpatterns = [
    path("", BatchAPI.as_view({"get": "listing"})),
    path("trigger/", BatchAPI.as_view({"post": "trigger"})),
]