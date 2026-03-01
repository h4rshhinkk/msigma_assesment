from django.urls import path
from .views import ReportAPI

urlpatterns = [
    path("status-metrics/", ReportAPI.as_view({"get": "status_metrics"})),
    path("stuck-candidates/", ReportAPI.as_view({"get": "stuck_candidates"})),
]