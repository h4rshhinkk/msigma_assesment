from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg
from django.db.models.functions import TruncDay, TruncWeek
from django.utils.dateparse import parse_datetime
from candidates.models import Candidate
from core.permissions import IsReviewerOrAdmin
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
# Create your views here.


class ReportAPI(ViewSet):
    permission_classes = [IsAuthenticated, IsReviewerOrAdmin]

    def status_metrics(self, request):
        qs = Candidate.objects.all()

        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        group_by = request.query_params.get("groupBy")
        include_domains = request.query_params.get("includeDomains")

        if from_date:
            qs = qs.filter(created_at__gte=parse_datetime(from_date))
        if to_date:
            qs = qs.filter(created_at__lte=parse_datetime(to_date))

        total = qs.count()
        success = qs.filter(status="SUCCESS").count()
        failed = qs.filter(status="FAILED").count()
        processed = success + failed
        success_rate = (success / processed) * 100 if processed else 0

        avg_attempt = qs.filter(status="SUCCESS").aggregate(
            Avg("attempt_count")
        )["attempt_count__avg"]

        retry_histogram = (
            qs.values("attempt_count")
            .annotate(count=Count("id"))
            .order_by("attempt_count")
        )

        
        if group_by == "day":
            grouped = qs.annotate(date=TruncDay("created_at")).values("date").annotate(count=Count("id"))
        elif group_by == "week":
            grouped = qs.annotate(date=TruncWeek("created_at")).values("date").annotate(count=Count("id"))
        else:
            grouped = []

        
        top_domains = []
        if include_domains == "true":
            domain_map = {}
            for c in qs.filter(status="SUCCESS"):
                domain = c.email.split("@")[1]
                domain_map[domain] = domain_map.get(domain, 0) + 1
            top_domains = domain_map

        return Response({
            "totalCreated": total,
            "processed": processed,
            "successCount": success,
            "failureCount": failed,
            "successRate": success_rate,
            "averageAttemptsToSuccess": avg_attempt,
            "retryDistribution": list(retry_histogram),
            "groupedData": list(grouped),
            "topDomains": top_domains
        })
    
    def stuck_candidates(self, request):
        N = int(request.query_params.get("minAttempts", 3))
        X = int(request.query_params.get("hoursFailed", 24))
        Y = int(request.query_params.get("hoursPending", 24))

        now = timezone.now()

        qs = Candidate.objects.filter(
            Q(status="FAILED",
            attempt_count__gte=N,
            created_at__lte=now - timedelta(hours=X))
            |
            Q(status="PENDING",
            attempt_count=0,
            created_at__lte=now - timedelta(hours=Y))
        )

        return Response({
            "count": qs.count(),
            "items": [
                {
                    "id": c.id,
                    "attemptCount": c.attempt_count,
                    "lastAttemptAt": c.created_at,
                    "ageHours": (now - c.created_at).total_seconds() / 3600,
                } for c in qs
            ]
        })