from rest_framework import serializers
from .models import BatchRun


class BatchRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchRun
        fields = [
            "id",
            "scheduled_for",
            "started_at",
            "finished_at",
            "batch_size",
            "success_count",
            "failed_count",
            "created_at",
        ]