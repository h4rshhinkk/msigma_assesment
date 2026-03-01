from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from rest_framework import status
from .models import BatchRun
from .serializers import BatchRunSerializer
from core.permissions import IsAdmin, IsReviewerOrAdmin
from batches.tasks import process_batch
# Create your views here.



class BatchAPI(ViewSet):
    permission_classes = [IsAuthenticated]

    def listing(self, request):
        if request.user.role not in ["ADMIN", "REVIEWER"]:
            return Response({"message": "Forbidden"}, status=403)

        qs = BatchRun.objects.all().order_by("-created_at")

        page_number = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pageSize", 20))

        paginator = Paginator(qs, page_size)
        page = paginator.get_page(page_number)

        serializer = BatchRunSerializer(page.object_list, many=True)

        return Response({
            "items": serializer.data,
            "page": page_number,
            "pageSize": page_size,
            "total": paginator.count
        })

    def trigger(self, request):
        if request.user.role != "ADMIN":
            return Response({"message": "Forbidden"}, status=403)

        process_batch.delay()
        return Response({"message": "Batch triggered successfully"})
    

