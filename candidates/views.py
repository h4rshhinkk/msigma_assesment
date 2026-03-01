from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from .models import Candidate
from .serializers import CandidateSerializer , CandidateSearchSerializer
from core.permissions import IsAdmin, IsReviewerOrAdmin
from django.db import IntegrityError
from django.core.paginator import Paginator
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

    def search(self, request):
        qs = Candidate.objects.all()

        q = request.query_params.get("q")
        status_param = request.query_params.getlist("status")
        created_from = request.query_params.get("createdFrom")
        created_to = request.query_params.get("createdTo")
        has_link = request.query_params.get("hasLink")
        min_attempts = request.query_params.get("minAttempts")
        sort = request.query_params.get("sort")

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q))

        if status_param:
            qs = qs.filter(status__in=status_param)

        if created_from:
            qs = qs.filter(created_at__gte=parse_datetime(created_from))

        if created_to:
            qs = qs.filter(created_at__lte=parse_datetime(created_to))

        if has_link == "true":
            qs = qs.exclude(link__isnull=True)
        elif has_link == "false":
            qs = qs.filter(link__isnull=True)

        if min_attempts:
            qs = qs.filter(attempt_count__gte=int(min_attempts))

        if sort == "recent":
            qs = qs.order_by("-created_at")
        elif sort == "attempts_desc":
            qs = qs.order_by("-attempt_count")
        elif sort == "status_then_recent":
            qs = qs.order_by("status", "-created_at")

        # Custom Pagination
        page_number = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pageSize", 20))

        paginator = Paginator(qs, page_size)
        page = paginator.get_page(page_number)

        serializer = CandidateSearchSerializer(page.object_list, many=True)

        return Response({
            "items": serializer.data,
            "page": page_number,
            "pageSize": page_size,
            "total": paginator.count,
        })