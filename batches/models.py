from django.db import models

# Create your models here.
class BatchRun(models.Model):
    scheduled_for = models.DateTimeField()
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

    batch_size = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)


class CandidateAttempt(models.Model):
    candidate = models.ForeignKey("candidates.Candidate", on_delete=models.CASCADE)
    batch_run = models.ForeignKey(BatchRun, on_delete=models.CASCADE)

    attempt_no = models.IntegerField()
    result_status = models.CharField(max_length=20)
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)