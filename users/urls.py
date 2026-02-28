from django.urls import path
from .views import AuthAPI

urlpatterns = [
    path("login/", AuthAPI.as_view({"post": "login"})),
    path("refresh/", AuthAPI.as_view({"post": "refresh"})),
    path("logout/", AuthAPI.as_view({"post": "logout"})),
]