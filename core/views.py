from django.shortcuts import render

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
# Create your views here.

class HealthAPI(ViewSet):
    permission_classes = [AllowAny]

    def listing(self, request):
        return Response({"status": "ok"})