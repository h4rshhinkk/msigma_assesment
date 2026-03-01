from django.urls import path
from .views import CandidateAPI

urlpatterns = [
    path("", CandidateAPI.as_view({"post": "create"})),
    
]