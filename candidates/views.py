from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from .models import Candidate
from .serializers import CandidateSerializer
from core.permissions import IsAdmin, IsReviewerOrAdmin
from django.db import IntegrityError
# Create your views here.

class CandidateAPI(ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsAdmin()]
        if self.action == "search":
            return [IsAuthenticated(), IsReviewerOrAdmin()]
        return super().get_permissions()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            instance = serializer.save()
        except IntegrityError:
            return Response(
                {"message": "Candidate with this email already exists"},
                status=409
            )

        return Response(
        {
        "id": instance.id,
        "message": "Candidate created successfully"
        ""
        }, status=201)